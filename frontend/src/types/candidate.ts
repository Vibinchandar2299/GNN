export interface Candidate {
  studentId: string;
  department: string;
  cgpa: number;
  backlogs: number;
  aptitudeScorePre: number;
  codingScorePre: number;
  communicationScorePre: number;
  projectsCount: number;
  internshipsCount: number;
  certificationsCount: number;
  resumeScore: number;
  skills: string[];
}
