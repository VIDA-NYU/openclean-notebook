/* This file is part of the Data Cleaning Library (openclean).
 *
 * Copyright (C) 2018-2020 New York University.
 *
 * openclean is released under the Revised BSD License. See file LICENSE for
 * full license details.
 */

/*
 * The request result contains all the information that is needed to render the
 * spreadsheet view.
 */
export interface RequestResult {
  columns: string[];
  dataset: Dataset;
  offset: number;
  rowCount: number;
  rows: Row[];
  metadata?: Metadata;
  library?: Library;
  version: string | null;
}

// -- Dataset -----------------------------------------------------------------

/*
 * The dataset identifier. A dataset is maintained by an openclean engine. The
 * dataset name is unique among all datasets that are maintained by the same
 * engine.
 */
export interface Dataset {
  engine: string;
  name: string;
}

export interface Row {
  id: number;
  values: string[];
}

// -- Library of registered objects -------------------------------------------

/*
 * Collections of objects that have been registered with the dataset engine. For
 * now we only consider user-defined functions. In the future we may also want
 * to visualize and manipulate other objects such as mapping tables, lists of
 * outlier values, etc.. via the front-end.
 */
export interface Library {
    functions: FunctionSpec[]
}

/*
 * Information about a registered function. Each function has a unique name
 * and belongs to an (optional) namespace. The combination of namespace and
 * name forms a unique key. For display purposes the function may have a label,
 * i.e., the display name, and a help string (e.g., for use as tooltip).
 *
 * For each function we specify the number of input columns that it operates on
 * and the number of output values. A function may accept additional input
 * parameters.
 */
export interface FunctionSpec {
    columns: number;
    help?: string;
    label?: string;
    name: string;
    namespace?: string;
    outputs: number;
    parameters: ParameterSpec[];
}

/*
 * Specification of additional function parameters. Each parameter has a data
 * type and a unique name. For display purposes, parameters may have an optional
 * display name (label) and a short descriptive help text. The parameter index
 * and parameter group identifier are used to group and order order parameters
 * in a UI form.
 */
export interface ParameterSpec {
    dtype: ParameterType;
    name: string;
    index: number;
    label?: string;
    help?: string;
    defaultValue: unknown;
    isRequired: boolean;
    group: string;
}

/* Enumeration of parameter types. */
enum ParameterType {
    PARA_BOOL = 'bool',
    PARA_FILE = 'file',
    PARA_FLOAT = 'float',
    PARA_INT = 'int',
    PARA_LIST = 'list',
    PARA_RECORD = 'record',
    PARA_SELECT = 'select',
    PARA_STRING = 'string',
}

/*
 * Reference (or identifier) for a registered command. Each command is uniquely
 * identified by the combination of command name and namespace.
 */
export interface CommandRef {
    name: string;
    namespace: string;
}

// -- Metadata ----------------------------------------------------------------

export interface Metadata {
    profiling: ProfilingResult;
    log: OpProv[];
}

/*
 * Profiling Metadata from the DataMart profiler.
 */
export interface ProfilingResult {
    id: number;
    columns: ColumnMetadata[];
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

/*
 * Descriptor for operators that have been applied to the dataset. Defines the
 * dataset provenance.
 *
 * Each operator in the dataset history contains a unique identifier, a serialization
 * of the operation name and arguments, and a flag that indicates whether the
 * operation has been ommitted (i.e., applied on the full dataset or not). An
 * operation that is not committed has only been applied on a sample of the
 * dataset and can therefore be rolled back. Committed operations currently cannot
 * be rolled back.
 */
export interface OpProv {
    id: string;
    op: OpDescriptor;
    isCommitted: boolean;
}

/*
 * Metadata for an operator that was applied to a dataset. In case of the LOAD
 * operator none of the properties except optype are known. For INSCOL and UPDATE
 * name and namespace reference the function that was applied, columns contains
 * the name of the modified columns. If the modified columns are different from
 * the input columns, sources will contain the names of the input columns.
 *
 * An INSCOL or UPDATE operator may also modify the target column by setting the
 * column values to a given constant values. In these cases name and namespace
 * will be missing in the descriptor but the value property will contain the
 * constant value.
 *
 * The insert position is only given for operators of type INSCOL.
 */
export interface OpDescriptor {
    optype: OpType,
    name?: string;
    namespace?: string;
    columns?: string[],
    sources?: string[],
    value?: unknown,
    pos?: number,
    parameters?: {name: string; value: string}[]
}

/* Enumeration of operator types. */
enum OpType {
    OP_INSCOL = 'inscol',
    OP_LOAD = 'load',
    OP_UPDATE = 'update',
    OP_SAMPLE = 'sample',
}

// -- Vega Plots Data ---------------------------------------------------------

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

export interface SpreadsheetData {
  metadata: ProfilingResult;
  sample: string[][];
}
