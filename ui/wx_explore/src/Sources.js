import React from "react";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Card from "react-bootstrap/Card";
import { getSources } from "./Api";

class Sources extends React.Component {
  state = {
    sources: [],
    loading: true,
    error: null,
  };

  componentDidMount() {
    getSources()
      .then((sources) => {
        this.setState({ sources, loading: false });
      })
      .catch((error) => {
        this.setState({ 
          error: "Failed to load weather sources", 
          loading: false 
        });
      });
  }

  render() {
    const { loading, error, sources } = this.state;

    if (loading) {
      return (
        <Container>
          <h2 className="mb-4">Weather Data Sources</h2>
          <div>Loading weather data sources...</div>
        </Container>
      );
    }

    if (error) {
      return (
        <Container>
          <h2 className="mb-4">Weather Data Sources</h2>
          <div className="alert alert-danger">{error}</div>
        </Container>
      );
    }

    return (
      <Container>
        <h2 className="mb-4">Weather Data Sources</h2>
        <Row>
          {sources.map((source) => (
            <Col key={source.id} md={6} lg={4} className="mb-4">
              <Card>
                <Card.Body>
                  <Card.Title>{source.name}</Card.Title>
                  <Card.Subtitle className="mb-2 text-muted">
                    {source.short_name}
                  </Card.Subtitle>
                  <Card.Text>
                    <strong>Coverage Area:</strong>
                    <br />
                    {source.coverage_area}
                    <br />
                    <br />
                    <strong>Update Frequency:</strong>
                    <br />
                    {source.update_frequency}
                    <br />
                    <br />
                    <strong>Resolution:</strong>
                    <br />
                    {source.resolution}
                  </Card.Text>
                  <Card.Link href={source.src_url} target="_blank">
                    Source Website
                  </Card.Link>
                </Card.Body>
              </Card>
            </Col>
          ))}
        </Row>
      </Container>
    );
  }
}

export default Sources;