
export interface PlayerStats {
  playerName: string;
  season: string;
  ppg: number;
  rpg: number;
  apg: number;
  spg: number;
  bpg: number;
  fgPercentage: number;
  threePPercentage: number;
  archetype: string;
  valuation: number;
  marketabilityScore: number;
}

export interface CareerMilestone {
  year: string;
  event: string;
  type: 'award' | 'milestone' | 'stat_peak';
}

export interface ContractScenario {
  teamName: string;
  years: number;
  totalValue: number;
  annualSalary: number;
  marketabilityImpact: number;
  fitScore: number;
}

export enum ChatMode {
  FAST = 'fast',
  THINK = 'think',
  LIVE = 'live'
}

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  mode?: ChatMode;
  timestamp: Date;
  data?: any; // To hold structured data from tools
}
