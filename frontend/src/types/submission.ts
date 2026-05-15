export interface SubmissionCreate {
  problem_id: string;
  code: string;
  language: string;
}

export interface Submission {
  id: string;
  problem_id: string;
  code: string;
  language: string;
  status: "pending" | "judging" | "accepted" | "failed" | "error";
  score?: number;
  runtime_ms?: number;
  memory_kb?: number;
  passed_count?: number;
  total_count?: number;
  error_message?: string;
  submitted_at: string;
  judged_at?: string;
}
