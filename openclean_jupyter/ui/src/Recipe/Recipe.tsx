import * as React from 'react';
import * as Icon from 'react-feather';
import { OpProv } from '../types';
import {Operator} from './../SpreadSheet';
interface RecipeProps {
    operatorProvenance: OpProv[];
    openRecipeDialog: () => void;
    onRollback: (id: string) => void;
    onCommit: () => void;
}
interface RecipeStates{
}
class Recipe extends React.PureComponent<RecipeProps, RecipeStates> {
    constructor(props: RecipeProps) {
        super(props);
    }
    isCommited(){
      const list = this.props.operatorProvenance.map(operator => operator.isCommitted);
      return list.some((element) => element)
    }

    render() {
        return (
            <div style={{flex: 'none', width: 250, marginRight:4,
          borderStyle: 'solid', borderWidth:1, borderColor:'#63518b'}}>
            <div className='d-flex justify-content-between flex-row'
            style={{backgroundColor: '#63518b', padding:4, position: 'sticky',
            top: '-1px',
            zIndex: 1}}
            >
              <div style={{color: 'white', fontSize:14, fontWeight:'bold'}}> Recipe </div>
              <div
                    className="btn-group btn-group-sm"
                    role="group"
                    aria-label="Basic example"
                    style={{
                      float: 'initial', fontSize: 12}}
                  >
              <button
                type="button"
                title="Apply changes to the full dataset"
                className="btn-gray active"
                style={{paddingTop:0, paddingBottom:0}}
                onClick={() => this.props.onCommit()}
                disabled={this.isCommited()}
              >
                Apply
              </button>
              <button
                type="button"
                title="Add this operator"
                className="btn-gray active"
                style={{paddingTop:0, paddingBottom:0}}
                onClick={() => this.props.openRecipeDialog()}
              >
                New
              </button>
              <button
                type="button"
                title="Export recipe"
                className="btn-gray active"
                style={{paddingTop:0, paddingBottom:0}}
                // onClick={() => props.onClick && props.onClick()}
              >
                Export
              </button></div>
            </div>
            <div style={{fontSize: 12, padding:4, height: 519, maxHeight: 519, overflow: 'auto'}}>
              Applied operators:
              <hr style={{marginTop: 6}}></hr>
              {this.props.operatorProvenance.length >0 && this.props.operatorProvenance.map(operator => (
                <div key={operator.id}>
                <span className={`badge badge-pill`}>
                  {operator.op.name}
                  {!operator.isCommitted &&
                    <button
                      type="button"
                      title="Remove this operator"
                      className="btn btn-link badge-corner-button"
                      onClick={() =>
                        this.props.onRollback(
                          operator.id
                        )
                      }
                    >
                      <Icon.XCircle size={13} />
                    </button>
                  }
                </span>
                <div>
                <ul>
                  {operator.op.name && <li>Operator: {operator.op.name}</li>}
                  {operator.op.optype && <li>Type: {operator.op.optype} </li>}
                  {operator.op.columns && <li>Column: {operator.op.columns && operator.op.columns[0]}</li>}
                </ul>
                </div>
                <hr></hr>
                </div>
              ))
              }
            </div>
          </div>
        )
    }
}

export {Recipe};