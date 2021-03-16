import React from 'react';
import ReactDOM from 'react-dom';
import {select} from 'd3-selection';
import 'regenerator-runtime/runtime';
import {SpreadSheet} from './SpreadSheet';

export function renderOpencleanVisBundle(divName: Element, data: string) {
  ReactDOM.render(<SpreadSheet data={data} />, select(divName).node());
}
