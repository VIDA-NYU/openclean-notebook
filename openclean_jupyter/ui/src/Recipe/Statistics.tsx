import * as React from 'react';
import Button from '@material-ui/core/Button';
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import Select from '@material-ui/core/Select';
import { CategoricalDataVegaFormat, FunctionSpec, OpProv, PlotVega, RequestResult } from '../types';
import { FormControlLabel, Switch, TextField } from '@material-ui/core';
import {VegaLite} from 'react-vega';
import {TopLevelSpec as VlSpec} from 'vega-lite';

export interface AppliedOperator {
    operatorName: string;
    operatorIndex: number;
    columnName: string;
    columnIndex: number;
    operator?: FunctionSpec;
    checked: boolean;
    newColumnName: string;
}
interface StatisticsState {
    selectedOperator: AppliedOperator;
}
interface StatisticsProps {
    result: RequestResult;
    handleDialogExecution: (selectedOperator: AppliedOperator) => void;
    closeRecipeDialog: () => void;
    operatorProvenance: OpProv[];
}


function getEncoding(typePlot: string | undefined) {
    const yContent = {
      field: 'count',
      type: 'quantitative',
      title: null,
    };
    if (typePlot === 'histogram_text') {
      return {
        y: {
          field: 'bin',
          type: 'ordinal',
          title: null,
        },
        x: {
          title: null,
          field: 'count',
          type: 'quantitative',
          sort: {order: 'descending', field: 'count'},
        },
        tooltip: [
          {field: 'bin', type: 'ordinal'},
          {field: 'count', type: 'quantitative'},
        ],
        actions: false,
      };
    } else {
      console.log('Unknown plot type ', typePlot);
      return;
    }
  }

function getSpecification(typePlot: string | undefined): VlSpec {
    const specification = {
      width: '120',
      data: {name: 'values'},
      description: 'A simple bar chart with embedded data.',
      encoding: getEncoding(typePlot),
      mark: 'bar',
      actions: false,
    };
    return specification as VlSpec;
  }

class Statistics extends React.PureComponent <StatisticsProps, StatisticsState> {
    constructor(props: StatisticsProps) {
        super(props);
        this.state = {
            selectedOperator: {
              operatorName: '',
              operatorIndex: 0,
              columnName: '',
              columnIndex: 0,
              checked: false,
              newColumnName: '',
            },
        };
        this.handleChangeNewColumnName = this.handleChangeNewColumnName.bind(this);
    }
    handleAddOperator(operatorIndex: number) {
        this.setState({
          selectedOperator: {
            ...this.state.selectedOperator,
            operatorIndex: operatorIndex,
            operator: this.props.result.library?.functions[operatorIndex]
          }
        });
    }
    handleAddColumn(columnIndex: number) {
        this.setState({selectedOperator: {...this.state.selectedOperator, columnIndex: columnIndex}});
    }

    handleChangeSwitch(eventName: string, isChecked: boolean) {
      this.setState({selectedOperator: {...this.state.selectedOperator, checked: isChecked}});
    };
    handleChangeNewColumnName(event: React.ChangeEvent<HTMLInputElement>) {
      const columnName = event.target.value;
      // Jupyter.keyboard_manager.disable()
      this.setState({selectedOperator: {...this.state.selectedOperator, newColumnName: columnName}});
    };

    // updateInputValue() {
    //   this.setState({selectedOperator: {...this.state.selectedOperator, newColumnName: columnName}});
    // }

    render(){
        const {operatorProvenance} = this.props;
        const typesOp: string []  = [];
        const operatorOp : string [] = [];
        const columnOp: string []  = [];

        this.props.operatorProvenance.length >0 && this.props.operatorProvenance.map(operator => {
            if (operator !== undefined && operator.op !== undefined && operator.op.optype !== undefined) {
                typesOp.push(operator.op.optype );
            }
            if (operator !== undefined && operator.op !== undefined && operator.op.name !== undefined) {
                operatorOp.push(operator.op.name );
            }
            if (operator !== undefined && operator.op !== undefined && operator.op.columns !== undefined && operator.op.columns !== null) {
                if(operator.op.columns[0] !== null ){
                    columnOp.push(operator.op.columns[0]);
                }
            }
        }
        );
        const totalStati = [typesOp, operatorOp, columnOp];
        var dataformarted_typesOp : CategoricalDataVegaFormat[] = []
        var dataformarted_operatorOp : CategoricalDataVegaFormat[] = []
        var dataformarted_columnOp : CategoricalDataVegaFormat[] = []
        for (var i=0; i <3; i++){
            var count: any = {};
            totalStati[i].forEach(function(i) { count[i] = (count[i]||0) + 1;});
            if(i==0){
                for (const el in count) { 
                    dataformarted_typesOp.push({count: count[el], bin: el});
                };
            }
            if(i==1){
                for (const el in count) { 
                    dataformarted_operatorOp.push({count: count[el], bin: el});
                };
            }
            if(i==2){
                for (const el in count) { 
                    dataformarted_columnOp.push({count: count[el], bin: el});
                };
            }
        }
        
        return (
            <div>
                <div style={{marginBottom: 25}}>
                <p><b>Updated columns: </b></p>
                <VegaLite
                    spec={getSpecification("histogram_text")}
                    data={{values: dataformarted_columnOp}}
                />
                </div>
                <div style={{marginBottom: 25}}>
                <p><b>Operators: </b></p>
                <VegaLite
                    spec={getSpecification("histogram_text")}
                    data={{values: dataformarted_operatorOp}}
                />
                </div>
                <div style={{marginBottom: 25}}>
                <p><b>Operator Types: </b></p>
                <VegaLite
                    spec={getSpecification("histogram_text")}
                    data={{values: dataformarted_typesOp}}
                />
                </div>
            </div>
        )
    }
}

export {Statistics};