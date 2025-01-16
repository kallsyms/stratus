import React from 'react';
import {AsyncTypeahead} from 'react-bootstrap-typeahead';
import debounce from 'lodash/debounce';
import axios from 'axios';

import Api from './Api';

const LocationResult = ({loc}) => (
  <div>
    <span>{loc.name}</span>
  </div>
);

export default class LocationSearchField extends React.Component {
  state = {
    isLoading: false,
    options: [],
    error: null,
  };

  // Track the latest request ID to handle out-of-order responses
  _requestId = 0;
  
  // Store the cancel token source
  _cancelTokenSource = null;

  componentWillUnmount() {
    // Cancel any pending requests when component unmounts
    if (this._cancelTokenSource) {
      this._cancelTokenSource.cancel('Component unmounted');
    }
  }

  // Create debounced search function
  _debouncedSearch = debounce((query) => {
    this._performSearch(query);
  }, 300);

  render() {
    return (
      <AsyncTypeahead
        {...this.state}
        placeholder="Location"
        minLength={3}
        onSearch={this._handleSearch}
        labelKey="name"
        renderMenuItemChildren={(option, props) => (
          <LocationResult key={option.id} loc={option} />
        )}
        onChange={(selected) => {
            if (selected.length > 0) {
                this.props.onChange(selected);
            }
        }}
      />
    );
  }

  _handleSearch = (query) => {
    // Reset error state and trigger debounced search
    this.setState({
      isLoading: true,
      error: null
    });
    this._debouncedSearch(query);
  }

  _performSearch = async (query) => {
    // Cancel any pending requests
    if (this._cancelTokenSource) {
      this._cancelTokenSource.cancel('New search initiated');
    }

    // Create new cancel token
    this._cancelTokenSource = axios.CancelToken.source();
    const currentRequestId = ++this._requestId;

    try {
      const { data } = await Api.get("/location/search", {
        params: { q: query },
        cancelToken: this._cancelTokenSource.token
      });

      // Only update state if this is the latest request
      if (currentRequestId === this._requestId) {
        this.setState({
          isLoading: false,
          options: data,
          error: null
        });
      }
    } catch (error) {
      // Ignore if cancelled or component unmounted
      if (!axios.isCancel(error)) {
        this.setState({
          isLoading: false,
          options: [],
          error: error.message || 'Failed to fetch locations'
        });
      }
    }
  }
}