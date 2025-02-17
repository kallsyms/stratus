import React from 'react';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Card from 'react-bootstrap/Card';
import Spinner from 'react-bootstrap/Spinner';

import Api from './Api';

export default class Sources extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      sources: null,
    };
  }

  componentDidMount() {
    Api.get("/sources").then(({data}) => {
      this.setState({sources: data});
    });
  }

  render() {
    if (this.state.sources == null) {
      return (
        <Spinner animation="border" role="status">
          <span className="sr-only">Loading...</span>
        </Spinner>
      );
    }

    return (
      <div>
        <Row className="justify-content-md-center">
          <Col md="auto">
            <h2>Weather Data Sources</h2>
          </Col>
        </Row>
        <Row>
          {this.state.sources.map(source => (
            <Col md={4} key={source.id} className="mb-4">
              <Card>
                <Card.Body>
                  <Card.Title>{source.name}</Card.Title>
                  <Card.Subtitle className="mb-2 text-muted">{source.short_name}</Card.Subtitle>
                  <Card.Text>
                    <strong>Coverage Area:</strong> {source.coverage_area}<br/>
                    <strong>Update Frequency:</strong> {source.update_frequency}<br/>
                    <strong>Resolution:</strong> {source.resolution}<br/>
                    <a href={source.src_url} target="_blank" rel="noopener noreferrer">Source Website</a>
                  </Card.Text>
                </Card.Body>
              </Card>
            </Col>
          ))}
        </Row>
      </div>
    );
  }
}