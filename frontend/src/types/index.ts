// User types
export interface User {
  email: string;
  full_name: string | null;
  role: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  captcha_id: string;
  captcha_text: string;
}

export interface CaptchaResponse {
  captcha_id: string;
  image_base64: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserUpdate {
  full_name?: string;
  password?: string;
}

// Agent types
export type AgentStatus = 'draft' | 'configured' | 'processing' | 'ready' | 'error';
export type ToolType = 'rag' | 'web_search' | 'custom_api';

export interface AgentToolConfig {
  tool_type: ToolType;
  tool_config?: Record<string, unknown>;
  is_enabled: boolean;
  sort_order: number;
}

export interface AgentToolResponse {
  id: string;
  tool_type: string;
  tool_config?: Record<string, unknown>;
  is_enabled: boolean;
  sort_order: number;
}

export interface Agent {
  id: string;
  name: string;
  description?: string;
  system_prompt?: string;
  template_id?: string;
  model_id?: string;
  embedding_model_id?: string;
  config?: Record<string, unknown>;
  status: AgentStatus;
  tools?: AgentToolResponse[];
  file_ids?: string[];
  sub_agent_ids?: string[];
  created_at: string;
  updated_at: string;
}

export interface AgentCreate {
  name: string;
  description?: string;
  system_prompt?: string;
  template_id?: string;
  model_id?: string;
  embedding_model_id?: string;
  config?: Record<string, unknown>;
  tools?: AgentToolConfig[];
  file_ids?: string[];
  sub_agent_ids?: string[];
  status?: string;
}

export interface AgentUpdate {
  name?: string;
  description?: string;
  system_prompt?: string;
  template_id?: string;
  model_id?: string;
  embedding_model_id?: string;
  config?: Record<string, unknown>;
  tools?: AgentToolConfig[];
  file_ids?: string[];
  sub_agent_ids?: string[];
  status?: string;
}

export interface AgentListResponse {
  agents: Agent[];
  total: number;
}

export interface AgentStatusResponse {
  status: string;
  tool_count: number;
  file_count: number;
  vector_count: number;
  is_ready: boolean;
}

export interface AgentTestRequest {
  query: string;
}

export interface AgentTestResponse {
  success: boolean;
  response?: string;
  tool_calls?: Record<string, unknown>[];
  token_usage?: Record<string, number>;
  latency_ms?: number;
  error?: string;
}

export interface AgentProcessRequest {
  force?: boolean;
}

export interface AgentProcessResponse {
  message: string;
  files_processed: number;
  chunks_created: number;
  status: string;
}

// Template types
export interface Template {
  id: string;
  name: string;
  description?: string;
  tool_config?: Record<string, unknown>;
  system_prompt_template?: string;
  category?: string;
  is_system: boolean;
  created_at: string;
  updated_at: string;
}

export interface TemplateCreate {
  name: string;
  description?: string;
  tool_config?: Record<string, unknown>;
  system_prompt_template?: string;
  category?: string;
  is_system?: boolean;
}

export interface TemplateUpdate {
  name?: string;
  description?: string;
  tool_config?: Record<string, unknown>;
  system_prompt_template?: string;
  category?: string;
}

export interface TemplateListResponse {
  templates: Template[];
  total: number;
}

// File types
export interface FileItem {
  id: string;
  filename: string;
  stored_filename: string;
  file_path: string;
  file_size?: number;
  mime_type?: string;
  created_at: string;
  updated_at: string;
}

export interface FileListResponse {
  files: FileItem[];
  total: number;
}

// Model types
export interface Model {
  id: string;
  name: string;
  provider: string;
  model_id: string;
  model_type: 'llm' | 'embedding';
  config?: Record<string, unknown>;
  pricing?: Record<string, unknown>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ModelListResponse {
  models: Model[];
  total: number;
}

export interface OpenRouterModel {
  id: string;
  name: string;
  description?: string;
  pricing?: Record<string, unknown>;
  context_length?: number;
}

export interface OpenRouterModelListResponse {
  models: OpenRouterModel[];
  total: number;
}

// Chat types
export interface ChatSession {
  id: string;
  agent_id: string;
  title?: string;
  created_at: string;
  updated_at: string;
}

export interface ChatSessionCreate {
  agent_id: string;
  title?: string;
}

export interface ChatSessionListResponse {
  sessions: ChatSession[];
  total: number;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  tool_calls?: Record<string, unknown>;
  token_usage?: Record<string, unknown>;
  created_at: string;
}

export interface ChatMessageCreate {
  content: string;
  config?: Record<string, unknown>;
}

export interface ChatMessageListResponse {
  messages: ChatMessage[];
  total: number;
}

// SSE Stream Event types (from agent ReAct loop)
export type StreamEventType =
  | 'thinking'
  | 'tool_start'
  | 'tool_result'
  | 'evaluation'
  | 'answer_token'
  | 'answer_end'
  | 'done'
  | 'error';

export interface ToolExecution {
  tool_type: string;
  tool_name: string;
  input?: Record<string, unknown>;
  output?: string;
  status: 'running' | 'completed' | 'error';
  started_at?: string;
  completed_at?: string;
  duration_ms?: number;
}

export interface StreamThinkingEvent {
  type: 'thinking';
  content: string;
}

export interface StreamToolStartEvent {
  type: 'tool_start';
  tool_type: string;
  tool_name: string;
  input: Record<string, unknown>;
}

export interface StreamToolResultEvent {
  type: 'tool_result';
  tool_type: string;
  tool_name: string;
  output: string;
  duration_ms: number;
}

export interface StreamEvaluationEvent {
  type: 'evaluation';
  score: number;
  reasoning: string;
  needs_retry: boolean;
}

export interface StreamAnswerTokenEvent {
  type: 'answer_token';
  content: string;
}

export interface StreamAnswerEndEvent {
  type: 'answer_end';
  message_id: string;
}

export interface StreamDoneEvent {
  type: 'done';
  total_tokens?: number;
  total_cost?: number;
}

export interface StreamErrorEvent {
  type: 'error';
  error: string;
}

export type StreamEvent =
  | StreamThinkingEvent
  | StreamToolStartEvent
  | StreamToolResultEvent
  | StreamEvaluationEvent
  | StreamAnswerTokenEvent
  | StreamAnswerEndEvent
  | StreamDoneEvent
  | StreamErrorEvent;

// Dashboard types
export interface PeriodInfo {
  start_date: string;
  end_date: string;
}

export interface DashboardSummary {
  total_calls: number;
  total_prompt_tokens: number;
  total_completion_tokens: number;
  total_tokens: number;
  total_cost: number;
  avg_latency_ms: number;
  agent_count: number;
  period: PeriodInfo;
}

export interface TimeseriesDataPoint {
  date: string;
  calls: number;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  cost: number;
}

export interface TimeseriesResponse {
  data: TimeseriesDataPoint[];
  period: PeriodInfo;
}

export interface AgentUsage {
  agent_id: string;
  agent_name: string;
  calls: number;
  total_tokens: number;
  cost: number;
}

export interface AgentUsageResponse {
  data: AgentUsage[];
  period: PeriodInfo;
}

// Dashboard query params
export interface DashboardQueryParams {
  start_date?: string;
  end_date?: string;
  agent_id?: string;
}
