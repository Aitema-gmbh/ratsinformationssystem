/**
 * aitema|RIS - API Client
 * Type-safe API client for the OParl REST API.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ===================================================================
// Types
// ===================================================================

export interface OParlListResponse<T> {
  data: T[];
  pagination: {
    totalElements: number;
    elementsPerPage: number;
    currentPage: number;
    totalPages: number;
  };
  links: {
    self: string;
    next?: string;
    prev?: string;
    first?: string;
    last?: string;
  };
}

export interface OParlMeeting {
  id: string;
  type: string;
  name?: string;
  meetingState?: string;
  cancelled?: boolean;
  start?: string;
  end?: string;
  location?: string;
  organization?: string[];
  participant?: string[];
  invitation?: string;
  resultsProtocol?: string;
  agendaItem?: string[];
  created?: string;
  modified?: string;
}

export interface OParlPaper {
  id: string;
  type: string;
  name: string;
  reference?: string;
  date?: string;
  paperType?: string;
  mainFile?: string;
  auxiliaryFile?: string[];
  originatorPerson?: string[];
  originatorOrganization?: string[];
  created?: string;
  modified?: string;
}

export interface OParlOrganization {
  id: string;
  type: string;
  name: string;
  shortName?: string;
  organizationType?: string;
  post?: string[];
  startDate?: string;
  endDate?: string;
  website?: string;
  classification?: string;
  membership?: string;
  created?: string;
  modified?: string;
}

export interface OParlPerson {
  id: string;
  type: string;
  name: string;
  familyName?: string;
  givenName?: string;
  formOfAddress?: string;
  gender?: string;
  email?: string[];
  phone?: string[];
  status?: string[];
  membership?: string[];
}

export interface OParlBody {
  id: string;
  type: string;
  name: string;
  shortName?: string;
  website?: string;
  ags?: string;
  classification?: string;
  organization?: string;
  person?: string;
  meeting?: string;
  paper?: string;
  legislativeTerm?: string;
}

export interface SearchResult {
  data: Array<{
    id: string;
    type: string;
    name: string;
    reference?: string;
    score: number;
    highlight?: Record<string, string[]>;
  }>;
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// ===================================================================
// API Client
// ===================================================================

class APIClient {
  private baseUrl: string;
  private token?: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
  }

  setToken(token: string) {
    this.token = token;
  }

  clearToken() {
    this.token = undefined;
  }

  private async request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };

    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${this.baseUrl}${path}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || `API Error: ${response.status}`);
    }

    return response.json();
  }

  // --- OParl Endpoints ---

  async getSystem() {
    return this.request<any>("/api/v1/oparl/system");
  }

  async getBodies(page = 1) {
    return this.request<OParlListResponse<OParlBody>>(
      `/api/v1/oparl/body?page=${page}`
    );
  }

  async getBody(bodyId: string) {
    return this.request<OParlBody>(`/api/v1/oparl/body/${bodyId}`);
  }

  async getMeetings(bodyId: string, page = 1) {
    return this.request<OParlListResponse<OParlMeeting>>(
      `/api/v1/oparl/body/${bodyId}/meeting?page=${page}`
    );
  }

  async getMeeting(meetingId: string) {
    return this.request<OParlMeeting>(`/api/v1/oparl/meeting/${meetingId}`);
  }

  async getPapers(
    bodyId: string,
    params: { page?: number; paperType?: string; q?: string } = {}
  ) {
    const searchParams = new URLSearchParams();
    searchParams.set("page", String(params.page || 1));
    if (params.paperType) searchParams.set("paper_type", params.paperType);
    if (params.q) searchParams.set("q", params.q);
    return this.request<OParlListResponse<OParlPaper>>(
      `/api/v1/oparl/body/${bodyId}/paper?${searchParams.toString()}`
    );
  }

  async getPaper(paperId: string) {
    return this.request<OParlPaper>(`/api/v1/oparl/paper/${paperId}`);
  }

  async getOrganizations(
    bodyId: string,
    params: { organizationType?: string } = {}
  ) {
    const searchParams = new URLSearchParams();
    if (params.organizationType) {
      searchParams.set("organization_type", params.organizationType);
    }
    const qs = searchParams.toString();
    return this.request<OParlListResponse<OParlOrganization>>(
      `/api/v1/oparl/body/${bodyId}/organization${qs ? `?${qs}` : ""}`
    );
  }

  async getOrganization(orgId: string) {
    return this.request<OParlOrganization>(
      `/api/v1/oparl/organization/${orgId}`
    );
  }

  async getPersons(bodyId: string, page = 1) {
    return this.request<OParlListResponse<OParlPerson>>(
      `/api/v1/oparl/body/${bodyId}/person?page=${page}`
    );
  }

  async search(query: string, params: { objectType?: string; bodyId?: string; page?: number } = {}) {
    const searchParams = new URLSearchParams({ q: query });
    if (params.objectType) searchParams.set("object_type", params.objectType);
    if (params.bodyId) searchParams.set("body_id", params.bodyId);
    searchParams.set("page", String(params.page || 1));
    return this.request<SearchResult>(
      `/api/v1/oparl/search?${searchParams.toString()}`
    );
  }
}

export const apiClient = new APIClient();
