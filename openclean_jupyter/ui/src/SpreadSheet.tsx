import * as React from 'react';
import CommAPI from './CommAPI';
import {ResquestResult, ColumnMetadata} from './types';
import {DatasetSample} from './DatasetSample';
interface TableSampleProps {
  data: string;
}
interface TableSampleState {
  result: ResquestResult;
}

class SpreadSheet extends React.PureComponent<
  TableSampleProps,
  TableSampleState
> {
  constructor(props: TableSampleProps) {
    super(props);
    this.commPowersetAnalysis = new CommAPI(
      'spreadsheet',
      (msg: ResquestResult) => {
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

  getMetadata(requestResult: ResquestResult) {
    const columnNames = [requestResult.columns.map(col => col.name)];
    const rowsValues = requestResult.rows.map(row => row.values);
    const columnsMetadata: ColumnMetadata[] = [];
    columnNames[0].forEach(col => {
      columnsMetadata.push({
        name: col,
        structural_type: 'undefined',
        semantic_types: [],
      });
    });
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

  render() {
    const hit = this.getMetadata(this.state.result);
    return (
      <div className="mt-2">
        <div className="d-flex flex-row">
          <DatasetSample hit={hit} />
        </div>
      </div>
    );
  }
}

export {SpreadSheet};
