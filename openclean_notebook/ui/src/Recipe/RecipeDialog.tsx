import * as React from 'react';
import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import Select from '@material-ui/core/Select';
import { AppliedOperator, FunctionSpec, RequestResult } from '../types';
import { FormControlLabel, Switch, TextField } from '@material-ui/core';

interface RecipeDialogState {
    selectedOperator: AppliedOperator;
}
interface RecipeDialogProps {
    result: RequestResult;
    handleDialogExecution: (selectedOperator: AppliedOperator) => void;
    dialogStatus: boolean;
    closeRecipeDialog: () => void;
}

class RecipeDialog extends React.PureComponent <RecipeDialogProps, RecipeDialogState> {
    constructor(props: RecipeDialogProps) {
        super(props);
        this.state = {
            selectedOperator: {
              operatorName: '',
              operatorIndex: 0,
              columnName: '',
              columnIndex: 0,
              checked: false,
              newColumnName: '',
              parameterValue: '',
              additionalColumn: '',
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
        const {result, dialogStatus} = this.props;
        return (
            <div>
            <Dialog
              open={dialogStatus}
              onClose={() => this.props.closeRecipeDialog()}
              aria-labelledby="alert-dialog-title"
              aria-describedby="alert-dialog-description"
            >
              <DialogTitle id="alert-dialog-title">{"Applying a new operator"}</DialogTitle>
              <DialogContent>
                <DialogContentText id="alert-dialog-description">
                  Select an operator and a column. The operator will be applied to the column values.
                </DialogContentText>
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
                      result.columns.map((colName, idx) => <MenuItem value={idx}>{colName}</MenuItem> )
                      }
                    </Select>
                    {/* </div>
  
                    <div style={{marginTop:6}}> */}
                    <InputLabel htmlFor="max-width">Operator</InputLabel>
                    <Select
                      autoFocus
                      value={this.state.selectedOperator.operatorIndex}
                      onChange={e => {
                        this.handleAddOperator(e.target.value as number);
                      }}
                    >
                      {
                      result.library && result.library.functions.map((lib, idx)=> <MenuItem value={idx}>{lib.name}</MenuItem> )
                      }
                    </Select>
                  </div>
                  <div>
                  <FormControlLabel
                      control={
                        <Switch
                          checked={this.state.selectedOperator.checked}
                          onChange={e => {this.handleChangeSwitch(e.target.name, e.target.checked)}}
                          name="checkedB"
                          color="primary"
                        />
                      }
                      label="Add as a new column"
                    />
                    {
                      this.state.selectedOperator.checked &&
                      <input
                        type="text"
                        name="search"
                        placeholder={'Column Name'}
                        value={this.state.selectedOperator.newColumnName}
                        onChange={event => this.handleChangeNewColumnName}
                      />
                      // <TextField id="outlined-basic" value={this.state.selectedOperator.newColumnName} onChange={event => this.handleChangeNewColumnName(event.target.value)} label="Column name" variant="outlined"/>
                    }
                    </div>
                </form>
              </DialogContent>
              <DialogActions>
                <Button onClick={() => this.props.closeRecipeDialog()} color="primary">
                  Cancel
                </Button>
                <Button onClick={() => this.props.handleDialogExecution(this.state.selectedOperator)} color="primary" autoFocus>
                  Apply
                </Button>
              </DialogActions>
            </Dialog>
          </div>
        )
    }
}

export {RecipeDialog};