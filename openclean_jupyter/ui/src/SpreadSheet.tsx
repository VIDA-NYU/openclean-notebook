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
        this.setState({result: msg});
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
      nb_profiled_rows: 0,
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

  onCommandClick(command: string, columnName: string) {
    this.commPowersetAnalysis.call({
      dataset: this.state.result.dataset,
      action: 'exec',
      command,
      args: {column: columnName},
    });
  }

  render() {
    const hit = this.getMetadata(this.state.result);

    return (
      <div className="mt-2">
        <div className="d-flex flex-row">
          <DatasetSample
            hit={hit}
            requestResult={this.state.result}
            onCommandClick={(command, columnName) => {
              this.onCommandClick(command, columnName);
            }}
          />
        </div>
      </div>
    );
  }
}

export {SpreadSheet};
