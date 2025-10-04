const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

interface ApiOptions extends RequestInit {
  token?: string;
}

export async function apiRequest<T>(
  endpoint: string,
  options: ApiOptions = {}
): Promise<T> {
  const { token, ...fetchOptions } = options;

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...fetchOptions,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}

// Auth API
export const authApi = {
  async login(email: string, password: string) {
    return apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  },

  async register(email: string, password: string, name?: string) {
    return apiRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, name }),
    });
  },

  async getCurrentUser(token: string) {
    return apiRequest('/auth/me', { token });
  },
};

// Chat API
export const chatApi = {
  async sendMessage(message: string, conversationId: string | null, token: string): Promise<any> {
    return apiRequest('/chat', {
      method: 'POST',
      token,
      body: JSON.stringify({ message, conversation_id: conversationId }),
    });
  },

  async getConversations(token: string): Promise<any[]> {
    return apiRequest('/conversations', { token });
  },

  async getConversationMessages(conversationId: string, token: string): Promise<any[]> {
    return apiRequest(`/conversations/${conversationId}/messages`, { token });
  },

  async deleteConversation(conversationId: string, token: string): Promise<any> {
    return apiRequest(`/conversations/${conversationId}`, {
      method: 'DELETE',
      token,
    });
  },
};

// Community API
export const communityApi = {
  async getCategories(): Promise<any[]> {
    return apiRequest('/community/categories');
  },

  async getPosts(skip = 0, limit = 10, categoryId?: string): Promise<any[]> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
      ...(categoryId && { category_id: categoryId }),
    });
    return apiRequest(`/community/posts?${params}`);
  },

  async getPost(postId: string) {
    return apiRequest(`/community/posts/${postId}`);
  },

  async createPost(title: string, content: string, categoryId: string, token: string) {
    return apiRequest('/community/posts', {
      method: 'POST',
      token,
      body: JSON.stringify({ title, content, category_id: categoryId }),
    });
  },

  async getComments(postId: string) {
    return apiRequest(`/community/posts/${postId}/comments`);
  },

  async createComment(postId: string, content: string, parentId: string | null, token: string) {
    return apiRequest(`/community/posts/${postId}/comments`, {
      method: 'POST',
      token,
      body: JSON.stringify({ content, parent_id: parentId }),
    });
  },
};

// User API
export const userApi = {
  async getProfile(token: string): Promise<any> {
    return apiRequest('/auth/me', { token });
  },

  async updateProfile(data: any, token: string): Promise<any> {
    return apiRequest('/auth/profile', {
      method: 'PUT',
      token,
      body: JSON.stringify(data),
    });
  },
};