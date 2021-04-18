import * as React from 'react';
import * as Icon from 'react-feather';
import { AppliedOperator, OpProv, RequestResult } from '../types';
import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
import Divider from '@material-ui/core/Divider';
import Box from '@material-ui/core/Box';
import { AddOperator } from './AddOperator';
import Snackbar from '@material-ui/core/Snackbar';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';
import { createStyles, Theme, withStyles, WithStyles } from '@material-ui/core/styles';
import AddCircleOutline from '@material-ui/icons/AddCircleOutline';
import History from '@material-ui/icons/History';
import Visibility from '@material-ui/icons/Visibility';
import PlayArrow from '@material-ui/icons/PlayArrow';
import GetAppIcon from '@material-ui/icons/GetApp';
// import VisibilityOutlinedIcon from '@material-ui/icons/VisibilityOutlined';
import Collapse from '@material-ui/core/Collapse';
import Button from '@material-ui/core/Button';
import Card from '@material-ui/core/Card';
import CardHeader from '@material-ui/core/CardHeader';
import CardContent from '@material-ui/core/CardContent';
import CardActions from '@material-ui/core/CardActions';
import { Statistics } from './Statistics';

interface TabPanelProps {
  children?: React.ReactNode;
  index: any;
  value: any;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`scrollable-auto-tabpanel-${index}`}
      aria-labelledby={`scrollable-auto-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box p={2}>
          {children}
        </Box>
      )}
    </div>
  );
}

const useStyles = (theme: Theme) => createStyles({
  root: {
    maxWidth: 345,
  },
  media: {
    height: 0,
    paddingTop: '56.25%', // 16:9
  },
  expand: {
    transform: 'rotate(0deg)',
    marginLeft: 'auto',
    transition: theme.transitions.create('transform', {
      duration: theme.transitions.duration.shortest,
    }),
  },
  expandOpen: {
    transform: 'rotate(180deg)',
  },
  button: {
    margin: theme.spacing(0),
  }
});

interface RecipeProps extends WithStyles<typeof useStyles>  {
    fetchData: (id: number, includeMetadata: boolean) => void;
    operatorProvenance: OpProv[];
    openRecipeDialog: () => void;
    onRollback: (id: number) => void;
    onCommit: () => void;
    result: RequestResult;
    handleDialogExecution: (selectedOperator: AppliedOperator) => void;
    closeRecipeDialog: () => void;
}
interface RecipeStates{
  tabValue: number;
  exportedTextsMessage: boolean;
  expanded: boolean;
}
class Recipe extends React.PureComponent<RecipeProps, RecipeStates> {
    constructor(props: RecipeProps) {
        super(props);
        this.state = {
          tabValue: 0,
          exportedTextsMessage: false,
          expanded: false,
        };
        this.handleChange = this.handleChange.bind(this);
    }
    isCommited(){
      const list = this.props.operatorProvenance.map(operator => operator.isCommitted);
      return list.some((element) => element)
    }
    handleChange = (event: React.ChangeEvent<{}>, newValue: number) => {
      this.setState({tabValue: newValue});
    };
    addOperator = (selectedOperator: AppliedOperator) => {
        this.setState({tabValue: 0, exportedTextsMessage: true, expanded: false});
        this.props.handleDialogExecution(selectedOperator);
    }
    handleExpandClick = () => {
      this.setState({expanded: true});
    };
    handleCloseClick = () => {
      this.setState({expanded: false});
      this.props.closeRecipeDialog();
    };

    render() {
        const {classes} = this.props;
        // Get identifier for the last version. For this operator, no rollback
        // option is shown.
        const lastVersion = this.props.operatorProvenance[this.props.operatorProvenance.length - 1].id
        // Get the version number for the operator for which the resulting
        // data is currently shown in the spreadsheet from the attribute
        // props.result.version. If the value is null the last version is
        // being shown.
        let versionShown = this.props.result.version;
        if (versionShown == null) {
            versionShown = lastVersion;
        }
        return (
            <div style={{flex: 'none', width: 300, marginRight:0}}>
            <div className='d-flex justify-content-between flex-row'
            style={{backgroundColor: '#63518b', padding:4, position: 'sticky',
            top: '-1px', zIndex: 1, borderStyle: 'solid', borderWidth:1, borderColor:'#63518b'}}
            >
              <div style={{color: 'white', fontSize:14, fontWeight:'bold'}}> Recipe </div>
              <div
                    className="btn-group btn-group-sm"
                    role="group"
                    aria-label="Basic example"
                    style={{
                      float: 'initial', fontSize: 12}}
                  >
              <Button
                variant="contained"
                color="default"
                size="small"
                title="Apply changes to the full dataset"
                className={classes.button}
                style={{padding: 1, marginRight: 5}}
                onClick={() => this.props.onCommit()}
                startIcon={<PlayArrow fontSize="small" style={{marginRight: '-3px'}} />}
                disabled={this.isCommited()}
              >
                Apply
              </Button>
              </div>

            </div>
            <div style={{borderStyle: 'solid', borderWidth:1, borderColor:'#D3D3D3', color: '#63518b'}}>
            <Tabs
              value={this.state.tabValue}
              onChange={this.handleChange}
              indicatorColor="primary"
              textColor="inherit"
              TabIndicatorProps={{style: {backgroundColor:'#63518b'}}}
              // variant="scrollable"
              // scrollButtons="auto"
            >
              <Tab label="Applied Operators" style={{marginLeft: '-25px' }}/>
              <Tab label="Statistics" style={{marginLeft: '-25px' }} />
            </Tabs>
            <Divider light={true} style={{color: 'gray', backgroundColor: 'lightgray'}}/>
            <TabPanel value={this.state.tabValue} index={0}>
              <div style={{fontSize: 12, paddingRight:5, marginTop: 0, marginRight:'-14px', height: 542, maxHeight: 542, overflow: 'auto'}}>
                {this.props.operatorProvenance.length >0 && this.props.operatorProvenance.map(operator => (
                  <>
                    <div
                      key={operator.id}
                      className="card shadow-sm d-flex flex-row"
                      style={{
                        background: operator.id !== versionShown ? '#fff' : '#f5f4fa',
                      }}
                    >
                      <div className="card-body d-flex flex-column" style={{minWidth: 250}}>
                        <div>
                            <span className={`badge badge-pill`}>
                                 {(operator.op.optype === 'load' || operator.op.optype === 'sample') && 'Load'}
                                {operator.op.name}
                            </span>
                            {!operator.isCommitted && operator.id !== lastVersion &&
                            <button
                                    type="button"
                                    title="Rollback all changes"
                                    className="btn btn-link"
                                    onClick={() => this.props.onRollback(parseInt(operator.id))}
                                    style={{ fontSize: 10, color: '#63518b'}}
                                >
                                  <History fontSize="small" style={{color: '#63518b', marginBottom: '-2px', marginRight:1}}/>
                                    Rollback
                                </button>
                            }
                            {operator.id !== versionShown &&
                                <button
                                    type="button"
                                    title="See current dataset"
                                    className="btn btn-link"
                                    style={{ fontSize: 10, color: '#63518b'}}
                                    onClick={() => this.props.fetchData(parseInt(operator.id), true)}
                                >
                                  <Visibility fontSize="small" style={{color: '#63518b', marginBottom: '-2px', marginRight:1}}/>
                                    View
                                </button>
                            }
                        </div>
                        <div style={{color: '#5e5e5e'}}>
                            <ul style={{listStyleType: "none", paddingLeft: 5, marginTop: 5}}>
                                {operator.op.name && <li><b>Operator</b>: {operator.op.name}</li>}
                                {operator.op.optype && <li><b>Type</b>: {operator.op.optype} </li>}
                                {operator.op.columns && <li><b>Column</b>: {operator.op.columns && operator.op.columns[0]}</li>}
                            </ul>
                        </div>
                      </div>
                      <div
                        className="d-flex align-items-stretch"
                        style={{cursor: 'pointer'}}
                        onClick={() => this.props.fetchData(parseInt(operator.id), false)}
                      >
                        <div style={{margin: 'auto 3px'}}>
                          <Icon.ChevronRight className="feather feather-lg" />
                        </div>
                      </div>
                    </div>
                    <hr></hr>
                    </>
                ))}
                {
                  !this.state.expanded &&
                  <div className="d-flex justify-content-center">
                  <Button
                  variant="contained"
                  color="default"
                  size="small"
                  className={classes.button}
                  style={{padding: 5, marginBottom: 5}}
                  onClick={this.handleExpandClick}
                  startIcon={<AddCircleOutline />}
                >
                  Add Operator
                </Button>
                </div>
                }
                <Collapse in={this.state.expanded} timeout="auto" unmountOnExit>
                <Card className={classes.root} style={{backgroundColor: '#dcdcdc', marginRight: 6}}>
                  <CardHeader
                    title="Add a new operator"
                  />
                  <CardContent>
                    <AddOperator
                      result={this.props.result}
                      handleDialogExecution={(selectedOperator: AppliedOperator) => {
                        this.addOperator(selectedOperator);
                      }}
                      closeRecipeDialog={this.handleCloseClick}
                    />
                  </CardContent>
                  <CardActions disableSpacing>
                  </CardActions>
                </Card>
                </Collapse>
              </div>
            </TabPanel>
            <TabPanel value={this.state.tabValue} index={1}>
              <Statistics
                result={this.props.result}
                handleDialogExecution={(selectedOperator: AppliedOperator) => {
                  this.addOperator(selectedOperator);
                }}
                closeRecipeDialog={() => this.props.closeRecipeDialog()}
                operatorProvenance={this.props.operatorProvenance}
              />
            </TabPanel>
            </div>
            <Snackbar open={this.state.exportedTextsMessage} onClose={() => {this.setState({exportedTextsMessage: false})}}
                message={"The new operator was successfully applied."}
                autoHideDuration={6000}
                action={<IconButton size="small" aria-label="close" color="inherit" onClick={() => this.setState({exportedTextsMessage: false})}>
                  <CloseIcon fontSize="small" />
                </IconButton>}
      />
          </div>
        )
    }
}
export default withStyles(useStyles, { withTheme: true })(Recipe);
// export {Recipe};
