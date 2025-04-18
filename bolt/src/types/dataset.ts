export interface Dataset {
  id: string;
  title: string;
  description: string;
  format: string;
  formatColor: string;
  url: string;
  publisher: string;
  updated: string;
  created: string;
  identifier: string;
  license: string;
  spatial: string;
  temporal: string;
  accessRights: string;
  categories: string[];
}

export interface FilterOption {
  value: string;
  label: string;
}