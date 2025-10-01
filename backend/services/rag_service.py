import os
from openai import OpenAI
from dotenv import load_dotenv
from pypdf import PdfReader
from supabase import Client
import uuid

from .. import crud, schemas

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = (
    "당신은 임산부·임신 예정자·영유아 관련 정책 정보를 안내하는 전문가입니다. "
    "반드시 한국어로 답변하고, 제공된 문서 내용을 벗어나 추측하지 마세요. "
    "답변에는 중요 근거를 요약해 포함하고, 가능한 경우 출처 파일 이름과 페이지를 괄호로 표시하십시오. "
    "맥락에 정보가 없으면 '정보를 찾을 수 없습니다.'라고 말하세요."
)

def _get_embedding(text: str, model="text-embedding-3-small"):
   text = text.replace("\n", " ")
   return client.embeddings.create(input = [text], model=model).data[0].embedding

def _chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200):
    if not text:
        return []
    tokens = text.split()
    if not tokens:
        return []

    chunks = []
    for i in range(0, len(tokens), chunk_size - overlap):
        chunk = " ".join(tokens[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def ingest_pdf(supabase: Client, file_path: str, policy_id: str, policy_title: str):
    """Processes a PDF, creates embeddings, and stores it in the database."""
    try:
        reader = PdfReader(file_path)
        chunks_to_create = []

        # Create the main policy entry first
        crud.create_policy(
            supabase,
            policy_id=policy_id,
            title=policy_title,
            description="", # Can be extracted or summarized later
            category="childcare", # Example category
            region="national", # Example region
            eligibility={}
        )

        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if not text:
                continue
            
            text_chunks = _chunk_text(text)
            
            for i, text_chunk in enumerate(text_chunks):
                embedding = _get_embedding(text_chunk)
                
                chunk_id = f"{policy_id}-p{page_num+1}-c{i+1}"
                metadata = {"source": policy_title, "page": page_num + 1}

                chunk_data = schemas.PolicyChunkCreate(
                    id=chunk_id,
                    doc_id=policy_id,
                    chunk_index=i,
                    content=text_chunk,
                    metadata=metadata,
                    embedding=embedding
                )
                chunks_to_create.append(chunk_data)

        if chunks_to_create:
            crud.create_policy_chunks(supabase, chunks=chunks_to_create)
        
        return {"status": "success", "policy_id": policy_id, "chunks_created": len(chunks_to_create)}

    except Exception as e:
        return {"status": "error", "message": str(e)}


def process_all_pdfs(supabase: Client, policy_id: str = None):
    """Process all downloaded PDFs or a specific PDF with RAG."""
    pdf_dir = os.path.join(os.getcwd(), 'data', 'pdfs', 'bokjiro')

    if not os.path.exists(pdf_dir):
        return {"status": "error", "message": f"PDF directory not found: {pdf_dir}"}

    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]

    if not pdf_files:
        return {"status": "error", "message": "No PDF files found"}

    print(f"📦 Found {len(pdf_files)} PDF files to process")

    results = []
    success_count = 0

    for idx, pdf_filename in enumerate(pdf_files):
        pdf_path = os.path.join(pdf_dir, pdf_filename)

        # Extract title from filename (remove .pdf extension and year prefix)
        policy_title = pdf_filename.replace('.pdf', '').strip()
        if policy_title.startswith('2025년 '):
            policy_title = policy_title[6:].strip()

        # Generate policy ID from filename
        generated_policy_id = f"bokjiro_{uuid.uuid4().hex[:8]}"

        print(f"\n📄 [{idx+1}/{len(pdf_files)}] Processing: {policy_title}")
        print(f"   File: {pdf_filename}")

        try:
            result = ingest_pdf(
                supabase=supabase,
                file_path=pdf_path,
                policy_id=generated_policy_id,
                policy_title=policy_title
            )

            if result["status"] == "success":
                print(f"   ✓ Success: {result['chunks_created']} chunks created")
                success_count += 1
            else:
                print(f"   ✗ Failed: {result.get('message', 'Unknown error')}")

            results.append({
                "filename": pdf_filename,
                "policy_id": generated_policy_id,
                "title": policy_title,
                **result
            })

        except Exception as e:
            print(f"   ✗ Error: {e}")
            results.append({
                "filename": pdf_filename,
                "policy_id": generated_policy_id,
                "title": policy_title,
                "status": "error",
                "message": str(e)
            })

    print(f"\n✅ RAG processing complete: {success_count}/{len(pdf_files)} files processed successfully")

    return {
        "status": "completed",
        "total_files": len(pdf_files),
        "success_count": success_count,
        "results": results
    }


def answer_question(supabase: Client, request: schemas.ChatRequest, user_id: uuid.UUID):
    """Answers a user's question using RAG."""

    # 1. Get embedding for the user's question
    query_embedding = _get_embedding(request.message)

    # 2. Find relevant document chunks
    relevant_chunks = crud.search_relevant_chunks(supabase, query_embedding, top_k=3)
    
    if not relevant_chunks:
        # Fallback if no chunks are found
        return schemas.ChatResponse(
            answer="관련 정보를 찾을 수 없습니다.",
            conversation_id=request.conversation_id or uuid.uuid4(), # Should be handled better
            sources=[]
        )

    # 3. Construct context and prompt
    # relevant_chunks is a list of dicts, not objects
    context_text = "\n\n---\n\n".join([
        f"Source: {chunk['doc_id']}, Page: {chunk['metadata'].get('page', 'N/A')}\n\n{chunk['content']}"
        for chunk in relevant_chunks
    ])

    user_message = (
        "Answer the user question using ONLY the context below. Quote relevant "
        "sections when helpful. If the context does not contain enough "
        f"information, respond with '정보를 찾을 수 없습니다.'.\n\n"
        f"Context:\n{context_text}\n\n"
        f"Question: {request.message}"
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    # 4. Call OpenAI to get an answer
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=messages,
        temperature=0.7,
    )

    ai_answer = response.choices[0].message.content

    # 5. Format sources
    sources = [
        schemas.RagSource(
            doc_id=chunk['doc_id'],
            page=chunk['metadata'].get('page') if chunk.get('metadata') else None,
            content=chunk['content'],
            score=chunk.get('similarity', 0.0)
        ) for chunk in relevant_chunks
    ]

    # 6. Save conversation (this logic should be in the router)
    # crud.create_message(...)
    
    # 7. Return response
    return schemas.ChatResponse(
        answer=ai_answer,
        conversation_id=request.conversation_id or uuid.uuid4(), # Placeholder
        sources=sources
    )
