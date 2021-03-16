import * as React from 'react';
import Button from '@material-ui/core/Button';
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import Select from '@material-ui/core/Select';
import { FunctionSpec, RequestResult } from '../types';
import { FormControlLabel, Switch, TextField } from '@material-ui/core';

export interface AppliedOperator {
    operatorName: string;
    operatorIndex: number;
    columnName: string;
    columnIndex: number;
    operator?: FunctionSpec;
    checked: boolean;
    newColumnName: string;
}
interface AddOperatorState {
    selectedOperator: AppliedOperator;
}
interface AddOperatorProps {
    result: RequestResult;
    handleDialogExecution: (selectedOperator: AppliedOperator) => void;
    closeRecipeDialog: () => void;
}

class AddOperator extends React.PureComponent <AddOperatorProps, AddOperatorState> {
    constructor(props: AddOperatorProps) {
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
        const {result} = this.props;
        return (
            <div>
            <div>
              <div>
                <div style={{marginBottom: 12}}>
                  Select an operator and a column. The operator will be applied to the column values.
                  </div>
                <form noValidate>
                  <div>
                    <InputLabel htmlFor="max-width">Column</InputLabel>
                    <Select
                      autoFocus
                      // value={this.state.selectedOperator.columnName}
                      value={this.state.selectedOperator.columnIndex}
                      onChange={e => {
                        this.handleAddColumn(e.target.value as number);
                      }}
                    >
                      {
                      result.columns.map((colName, idx) => <MenuItem key={idx} value={idx}>{colName}</MenuItem> )
                      }
                    </Select>
                    </div>

                    <div style={{marginTop:6}}>
                    <InputLabel htmlFor="max-width">Operator</InputLabel>
                    <Select
                      autoFocus
                      value={this.state.selectedOperator.operatorIndex}
                      onChange={e => {
                        this.handleAddOperator(e.target.value as number);
                      }}
                    >
                      {
                      result.library && result.library.functions.map((lib, idx)=> <MenuItem key={idx} value={idx}>{lib.name}</MenuItem> )
                      }
                    </Select>
                  </div>
                  <div style={{marginTop:6}}>
                  <FormControlLabel
                      control={
                        <Switch
                          checked={this.state.selectedOperator.checked}
                          size="small"
                          onChange={e => {this.handleChangeSwitch(e.target.name, e.target.checked)}}
                          name="checkedB"
                          color="primary"
                        />
                      }
                      label="Add as a new column"
                    />
                    {
                      this.state.selectedOperator.checked &&
                      <TextField
                        id="outlined-basic"
                        size="small"
                        value={this.state.selectedOperator.newColumnName}
                        onChange={(event:React.ChangeEvent<HTMLInputElement>)  => this.handleChangeNewColumnName(event)}
                        label="Column name"
                        variant="outlined"
                      />
                    }
                    </div>
                </form>
              </div>
              <div style={{marginTop: 3}}>
                <Button onClick={() => this.props.closeRecipeDialog()} color="primary">
                  Cancel
                </Button>
                <Button onClick={() => this.props.handleDialogExecution(this.state.selectedOperator)} color="primary" autoFocus>
                  Apply
                </Button>
              </div>
            </div>
          </div>
        )
    }
}

export {AddOperator};
