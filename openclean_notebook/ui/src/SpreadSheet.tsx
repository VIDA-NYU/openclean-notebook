/* This file is part of the Data Cleaning Library (openclean).
 *
 * Copyright (c) 2018-2021 New York University.
 *
 * openclean is released under the Revised BSD License. See file LICENSE for
 * full license details.
 */

import * as React from 'react';
import CommAPI from './CommAPI';
import {
  AppliedOperator,
  Arg,
  CommandRef,
  FunctionRef,
  FunctionSpec,
  ProfilingResult,
  RequestResult,
  SpreadsheetData,
} from './types';
import {DatasetSample} from './DatasetSample';
import './SpreadSheet.css';
import Recipe from './Recipe/Recipe';

interface TableSampleProps {
  data: string;
}

interface TableSampleState {
  result: RequestResult;
  appliedOperators: Operator[];
  recipeDialogStatus: boolean;
}
export interface Operator {
  name: string;
  column: string;
}

class SpreadSheet extends React.PureComponent<
  TableSampleProps,
  TableSampleState
> {
  commSpreadsheetApi: CommAPI;
  constructor(props: TableSampleProps) {
    super(props);
    // Register callback handler for all messages received from the
    // spreadsheet API.
    this.commSpreadsheetApi = new CommAPI(
      'spreadsheet',
      (msg: RequestResult) => {
        // Each received message will contain the dataset identifier,
        // list  of column names, list of dataset rows, the row offset
        // and the total row count.
        //
        // The list of registered commands (msg.library) and  dataset
        // metadata (.msg.metadata) are optional components of the
        // received response. If present, the metadata object will have
        // the profling results (.profiling) and the list of applied
        // commands that define the history of the dataset (.log).
        this.setState({result: {...this.state.result, ...msg}});
      }
    );
    // Set the initial component state.
    this.state = {
      result: {
        dataset: {engine: '', name: ''},
        columns: [],
        offset: 0,
        rowCount: 0,
        rows: [],
        // library: [],
        // metadata: {}
        version: null,
      },
      appliedOperators: [],
      recipeDialogStatus: false,
    };
    // Initial call to the spreadsheet API that fetches the dataset schema,
    // the first 10 dataset rows, the profiling results (includeMetadata: true),
    // and the list of registered functions (includeLibrary: true).
    this.commSpreadsheetApi.call({
      dataset: this.props.data,
      fetch: {
        includeLibrary: true,
        includeMetadata: true,
      },
    });
    this.fetchData = this.fetchData.bind(this);
    this.openRecipeDialog = this.openRecipeDialog.bind(this);
    this.closeRecipeDialog = this.closeRecipeDialog.bind(this);
    this.onRollback = this.onRollback.bind(this);
  }

  /*
   * Fetch data for dataset snapshot with the given identfier.
   */
  fetchData(logEntryId: number, limit: number, includeMetadata: boolean) {
    this.commSpreadsheetApi.call({
      dataset: this.props.data,
      fetch: {
        offset: 0,
        limit: limit,
        version: logEntryId,
        includeMetadata: includeMetadata,
      },
    });
  }

  /*
   * Create a spreadsheet data object that contains the column names and row
   * sample together with the optional profiler results.
   */
  getSpreadsheetData(requestResult: RequestResult): SpreadsheetData {
    const columnNames = [requestResult.columns.map(col => col)];
    const rowsValues = requestResult.rows.map(row => row.values);

    let metadata = {};
    if (requestResult.metadata && requestResult.metadata.profiling) {
      const profile = requestResult.metadata.profiling;
      metadata = {
        id: profile.id,
        columns: profile.columns,
      };
    }

    return {
      metadata: metadata as ProfilingResult,
      sample: columnNames.concat(rowsValues),
    };
  }

  /*
   * Adding the attributes sources and args if they exist
   */
  setSourceArgs(
    selectedOperator: AppliedOperator,
    functionRef: FunctionRef
  ): FunctionRef {
    if (
      selectedOperator &&
      selectedOperator.sources &&
      selectedOperator.sources.length > 1
    ) {
      functionRef['sources'] = selectedOperator.sources;
    }
    const parameters: Arg[] = [];
    if (
      selectedOperator &&
      selectedOperator.parameters &&
      selectedOperator.parameters.length > 0
    ) {
      selectedOperator.parameters.map(para => {
        const parameter = {name: para.name, value: para.value};
        parameters.push(parameter);
      });
      functionRef['args'] = parameters;
    }
    return functionRef;
  }

  /*
   * Apply a given update operation on the dataset. The response will contain
   * the modified data rows and the updated profiling results and command log.
   */
  onCommandClick(
    command: FunctionSpec,
    columnIndex: number,
    limit: number,
    selectedOperator: AppliedOperator | undefined
  ) {
    let newColumnName = '';
    let addColumn = false;

    if (selectedOperator !== undefined) {
      columnIndex = selectedOperator.columnIndex;
      addColumn = selectedOperator.checked;
      newColumnName = selectedOperator.newColumnName;
    }
    const newOperator: Operator = {name: command.name, column: 'columnName'};
    let temp = this.state.appliedOperators;
    if (temp.length > 0) {
      temp.push(newOperator);
    } else {
      temp = [newOperator];
    }
    this.setState({appliedOperators: temp, recipeDialogStatus: false});

    const commandRef: CommandRef = {
      name: command.name,
      namespace: command.namespace ? command.namespace : '',
    };

    let payload = null;
    if (addColumn) {
      let functionRef: FunctionRef = {
        names: [newColumnName],
        sources: [columnIndex],
        values: commandRef,
      };
      if (selectedOperator) {
        functionRef = this.setSourceArgs(selectedOperator, functionRef);
      }
      payload = {
        dataset: this.props.data,
        action: {
          type: 'inscol',
          payload: functionRef,
        },
        fetch: {
          offset: this.state.result.offset,
          limit: limit,
        },
      };
      this.commSpreadsheetApi.call(payload);
    } else {
      let functionRef: FunctionRef = {
        columns: [columnIndex],
        func: commandRef,
      };
      if (selectedOperator) {
        functionRef = this.setSourceArgs(selectedOperator, functionRef);
      }
      payload = {
        dataset: this.props.data,
        action: {
          type: 'update',
          payload: functionRef,
        },
        fetch: {
          offset: this.state.result.offset,
          limit: limit,
        },
      };
    }
    this.commSpreadsheetApi.call(payload);
  }

  /*
   * Commit all changes that were applied on a dataset sample to the full
   * dataset.
   */
  onCommit(limit: number) {
    this.commSpreadsheetApi.call({
      dataset: this.props.data,
      action: {
        type: 'commit',
      },
      fetch: {
        offset: this.state.result.offset,
        limit: limit,
      },
    });
  }

  /*
   * Fetch rows from the backend.
   */
  onPageClick(offset: number, limit: number) {
    this.commSpreadsheetApi.call({
      dataset: this.props.data,
      fetch: {
        offset: offset,
        limit: limit,
        version: this.state.result.version,
      },
    });
  }

  openRecipeDialog() {
    this.setState({recipeDialogStatus: true});
  }
  closeRecipeDialog() {
    this.setState({recipeDialogStatus: false});
  }

  /*
   * Rollback all changes to the log entry with the given identfier.
   */
  onRollback(logEntryId: number, limit: number) {
    this.commSpreadsheetApi.call({
      dataset: this.props.data,
      action: {
        type: 'rollback',
        payload: logEntryId,
      },
      fetch: {
        offset: this.state.result.offset,
        limit: limit,
      },
    });
  }

  render() {
    const hit = this.getSpreadsheetData(this.state.result);
    const defaultLimit = 10;

    return (
      <>
        <div className="mt-2">
          <div className="d-flex flex-row">
            {this.state.result.metadata && (
              <Recipe
                fetchData={(id: number, includeMetadata: boolean) => {
                  this.fetchData(id, defaultLimit, includeMetadata);
                }}
                operatorProvenance={this.state.result.metadata.log}
                openRecipeDialog={() => this.openRecipeDialog()}
                onRollback={(id: number) => {
                  this.onRollback(id, defaultLimit);
                }}
                onCommit={() => this.onCommit(defaultLimit)}
                result={this.state.result}
                handleDialogExecution={(selectedOperator: AppliedOperator) => {
                  selectedOperator.operator &&
                    this.onCommandClick(
                      selectedOperator.operator,
                      selectedOperator.columnIndex,
                      defaultLimit,
                      selectedOperator
                    );
                }}
                closeRecipeDialog={() => this.closeRecipeDialog()}
              />
            )}
            <DatasetSample
              hit={hit}
              requestResult={this.state.result}
              onCommandClick={(command, columnIndex) => {
                this.onCommandClick(
                  command,
                  columnIndex,
                  defaultLimit,
                  undefined
                );
              }}
              onPageClick={offset => {
                this.onPageClick(offset, defaultLimit);
              }}
              pageSize={defaultLimit}
            />
          </div>
        </div>
      </>
    );
  }
}
export {SpreadSheet};
