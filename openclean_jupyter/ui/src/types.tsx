export interface RequestResult {
  columns: Column[];
  commands: string[];
  dataset: Dataset;
  offset: number;
  row_count: number;
  rows: Row[];
}
export interface Column {
  id: number;
  name: string;
}
export interface Dataset {
  engine: string;
  name: string;
}
export interface Row {
  id: number;
  values: string[];
}

export interface AugmentationTask {
  data: SearchResult;
}

export interface ColumnAggregations {
  [columnName: string]: string[];
}

// Keep in sync with datamart_profiler's temporal_aggregation_keys
export enum TemporalResolution {
  YEAR = 'year',
  QUARTER = 'quarter',
  MONTH = 'month',
  WEEK = 'week',
  DAY = 'day',
  HOUR = 'hour',
  MINUTE = 'minute',
  SECOND = 'second',
}

export interface AugmentationInfo {
  type: string;
  left_columns: number[][];
  left_columns_names: string[][];
  right_columns: number[][];
  right_columns_names: string[][];
  agg_functions?: ColumnAggregations;
  temporal_resolution?: TemporalResolution;
}

export interface SpatialCoverage {
  lat?: string;
  lon?: string;
  address?: string;
  point?: string;
  admin?: string;
  ranges: Array<{
    range: {
      coordinates: [[number, number], [number, number]];
      type: 'envelope';
    };
  }>;
}

export interface Metadata {
  id: string;
  filename?: string;
  name: string;
  description: string;
  size: number;
  nb_rows: number;
  columns: ColumnMetadata[];
  date: string;
  materialize: {};
  nb_profiled_rows: number;
  sample: string;
  source: string;
  types: string[];
  version: string;
  spatial_coverage?: SpatialCoverage[];
}

export interface ColumnMetadata {
  name: string;
  structural_type: string;
  semantic_types: string[];
  num_distinct_values?: number;
  coverage?: Array<{}>;
  mean?: number;
  stddev?: number;
  plot?: PlotVega;
  temporal_resolution?: string;
  latlong_pair?: string;
}

export interface PlotVega {
  type: string;
  data:
    | NumericalDataVegaFormat[]
    | TemporalDataVegaFormat[]
    | CategoricalDataVegaFormat[];
}
export interface NumericalDataVegaFormat {
  count: number;
  bin_start: number;
  bin_end: number;
}

export interface TemporalDataVegaFormat {
  count: number;
  date_start: string;
  date_end: string;
}

export interface CategoricalDataVegaFormat {
  count: number;
  bin: string;
}

export interface SearchResult {
  id: string;
  score: number;
  metadata: Metadata;
  augmentation?: AugmentationInfo;
  sample: string[][];
}
