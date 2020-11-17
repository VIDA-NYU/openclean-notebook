import * as React from 'react';
import CommAPI from './CommAPI';
import {RequestResult, ColumnMetadata} from './types';
import {DatasetSample} from './DatasetSample';
interface TableSampleProps {
  data: string;
}
interface TableSampleState {
  result: RequestResult;
}
class SpreadSheet extends React.PureComponent<
  TableSampleProps,
  TableSampleState
> {
  commPowersetAnalysis: CommAPI;
  constructor(props: TableSampleProps) {
    super(props);
    this.commPowersetAnalysis = new CommAPI(
      'spreadsheet',
      (msg: RequestResult) => {
        if (msg.metadata) {
          this.setState({result: msg});
        } else {
          this.setState({result: {...this.state.result, rows: msg.rows}});
        }
      }
    );
    this.commPowersetAnalysis.call({dataset: this.props.data, action: 'load'});
    this.state = {
      result: {
        columns: [],
        commands: [],
        dataset: {
          engine: '',
          name: '',
        },
        offset: 0,
        row_count: 0,
        rows: [],
      },
    };
  }

  getMetadata(requestResult: RequestResult) {
    const columnNames = [requestResult.columns.map(col => col.name)];
    const rowsValues = requestResult.rows.map(row => row.values);

    const columnsMetadata: ColumnMetadata[] = requestResult.metadata ? requestResult.metadata.columns : [];
    const metadata = {
      id: 'id',
      name: 'dataset',
      description: 'string',
      size: 0,
      nb_rows: requestResult.row_count,
      columns: columnsMetadata,
      date: '',
      materialize: {},
      nb_profiled_rows: requestResult.metadata ? requestResult.metadata.nb_profiled_rows : 0,
      sample: '',
      source: 'histore',
      types: [],
      version: '',
    };
    const hit = {
      id: 'id',
      score: 0,
      metadata: metadata,
      sample: columnNames.concat(rowsValues),
    };
    return hit;
  }

  onCommandClick(command: string, columnName: string, limit: number) {
    this.commPowersetAnalysis.call({
      dataset: this.state.result.dataset,
      action: 'exec',
      offset: this.state.result.offset,
      limit: limit,
      profiler: false,
      command,
      args: {column: columnName},
    });
  }

  onPageClick(offset: number, limit: number) {
    this.setState({result: {...this.state.result, offset: offset}});
    this.commPowersetAnalysis.call({
      dataset: this.props.data,
      action: 'fetch',
      profiler: false,
      offset: offset,
      limit: limit,
    });
  }

  render() {
    const hit = this.getMetadata(this.state.result);
    const defaultLimit = 10;
    return (
      <div className="mt-2">
        <div className="d-flex flex-row">
          <DatasetSample
            hit={hit}
            requestResult={this.state.result}
            onCommandClick={(command, columnName) => {
              this.onCommandClick(command, columnName, defaultLimit);
            }}
            onPageClick={(offset) => {
              this.onPageClick(offset, defaultLimit);
            }}
            pageSize={defaultLimit}
          />
        </div>
      </div>
    );
  }
}

export {SpreadSheet};
