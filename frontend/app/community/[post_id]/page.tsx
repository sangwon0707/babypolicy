export default function PostPage({ params }: { params: { post_id: string } }) {
  return <div>Post Page: {params.post_id}</div>;
}
