/* This file is part of the Data Cleaning Library (openclean).
 *
 * Copyright (C) 2018-2020 New York University.
 *
 * openclean is released under the Revised BSD License. See file LICENSE for
 * full license details.
 */

import * as React from 'react';
import CommAPI from './CommAPI';
import { CommandRef, RequestResult } from './types';
import {DatasetSample} from './DatasetSample';


interface TableSampleProps {
  data: string;
}

interface TableSampleState {
    result: RequestResult;
}


class SpreadSheet extends React.PureComponent<TableSampleProps, TableSampleState> {
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
        });
        // Set the initial component state.
        this.state = {
            result: {
                dataset: {engine: '', name: '',},
                columns: [],
                offset: 0,
                rowCount: 0,
                rows: [],
                library: [],
                metadata: {}
            }
        };
        // Initial call to the spreadsheet API that fetches the dataset schema,
        // the first 10 dataset rows, the profiling results (includeMetadata: true),
        // and the list of registered functions (includeLibrary: true).
        this.commSpreadsheetApi.call({
            dataset: this.props.data,
            fetch: {
                includeLibrary: true,
                includeMetadata: true
            }
        });
    }

    /*
     * Create a spreadsheet data object that contains the column names and row
     * sample together with the optional profiler results.
     */
    getSpreadsheetData(requestResult: RequestResult) {
        const columnNames = [requestResult.columns.map(col => col)];
        const rowsValues = requestResult.rows.map(row => row.values);

        let metadata = [];
        if (requestResult.metadata.profiling) {
            const profile = requestResult.metadata.profiling;
            metadata = {
                id: profile.id,
                columns: profile.columns
            }
        }

        return {
            metadata: metadata,
            sample: columnNames.concat(rowsValues),
        };
    }

    /*
     * Apply a given update operation on the dataset. The response will contain
     * the modified data rows and the updated profiling results and command log.
     */
    onCommandClick(command: CommandRef, columnIndex: number, limit: number) {
        this.commSpreadsheetApi.call({
            dataset: this.props.data,
            action: {
                type: 'update',
                payload: {
                    columns: [columnIndex],
                    func: command
                }
            },
            fetch: {
                offset: this.state.result.offset,
                limit: limit
            }
        });
    }

    /*
    * Commit all changes that were applied on a dataset sample to the full
    * dataset.
    */
    onCommit(limit: number) {
        this.commSpreadsheetApi.call({
            dataset: this.props.data,
            action: {
                type: 'commit'
            },
            fetch: {
                offset: this.state.result.offset,
                limit: limit
            }
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
                limit: limit
            }
        });
    }

    /*
    * Rollback all changes to the log entry with the given identfier.
    */
    onRollback(logEntryId: string, limit: number) {
        this.commSpreadsheetApi.call({
            dataset: this.props.data,
            action: {
                type: 'rollback',
                payload: logEntryId
            },
            fetch: {
                offset: this.state.result.offset,
                limit: limit
            }
        });
    }

    render() {
        const hit = this.getSpreadsheetData(this.state.result);
        const defaultLimit = 10;
        const log = this.state.result.metadata.log;
        // Add opertion log and commit button (for test purposes).
        const opList = [];
        let hasUncommitted = false;
        if (log != null) {
            log.map(e => {
                let op = e.op;
                let name = op.optype;
                if (op.name) {
                    name += ' - ' + op.name;
                }
                let handleRollback = null;
                if (!e.isCommitted) {
                    hasUncommitted = true;
                    handleRollback = () => (this.onRollback(e.id, defaultLimit));
                }
                opList.push(<p key={e.id} onClick={handleRollback}>{name}</p>);
            });
        }
        return (
            <div className="mt-2">
                <div className="d-flex flex-row">
                    <DatasetSample
                        hit={hit}
                        requestResult={this.state.result}
                        onCommandClick={(command, columnIndex) => {
                            this.onCommandClick(command, columnIndex, defaultLimit);
                        }}
                        onPageClick={(offset) => {
                            this.onPageClick(offset, defaultLimit);
                        }}
                        pageSize={defaultLimit}
                    />
                    <div>
                        <h3>Recipe</h3>
                        { opList }
                    </div>
                    <button
                        type='button'
                        onClick={() => (this.onCommit(defaultLimit))}
                        disabled={!hasUncommitted}
                    >
                        Save
                    </button>
                </div>
            </div>
        );
    }
}

export {SpreadSheet};
