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
import { RequestResult } from '../types';

export interface AppliedOperator {
    operator: string;
    columnName: string;
}
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
            selectedOperator: {operator: '', columnName: ''},
        }
    }
    handleAddOperator(operator: string) {
        this.setState({selectedOperator: {...this.state.selectedOperator, operator: operator}});
    }
    handleAddColumn(columnName: string) {
        this.setState({selectedOperator: {...this.state.selectedOperator, columnName: columnName}});
    }
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
                      value={this.state.selectedOperator.columnName}
                      onChange={e => {
                        this.handleAddColumn(e.target.value as string);
                      }}
                    >
                      {
                      result.columns.map(col => <MenuItem value={col.name}>{col.name}</MenuItem> )
                      }
                    </Select>
                    </div>
  
                    <div style={{marginTop:6}}>
                    <InputLabel htmlFor="max-width">Operator</InputLabel>
                    <Select
                      autoFocus
                      value={this.state.selectedOperator.operator}
                      onChange={e => {
                        this.handleAddOperator(e.target.value as string);
                      }}
                    >
                      {
                      result.commands.map(command => <MenuItem value={command}>{command}</MenuItem> )
                      }
                    </Select>
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