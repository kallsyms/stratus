import React, { useState, useEffect } from "react";
import { getSources } from "./Api";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Card from "react-bootstrap/Card";
import Table from "react-bootstrap/Table";
import Spinner from "react-bootstrap/Spinner";
import Alert from "react-bootstrap/Alert";

const Sources = () => {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSources = async () => {
      try {
        const response = await getSources();
        setSources(response.data);
        setLoading(false);
      } catch (err) {
        console.error("Error fetching sources:", err);
        setError("Failed to load weather model sources. Please try again later.");
        setLoading(false);
      }
    };

    fetchSources();
  }, []);

  if (loading) {
    return (
      <Container className="text-center mt-5">
        <Spinner animation="border" role="status">
          <span className="sr-only">Loading...</span>
        </Spinner>
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="mt-3">
        <Alert variant="danger">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container className="mt-3">
      <h1 className="mb-4">Weather Model Sources</h1>
      <Row>
        {sources.map((source) => (
          <Col key={source.id} md={12} className="mb-4">
            <Card>
              <Card.Header as="h5">{source.name}</Card.Header>
              <Card.Body>
                <Table striped bordered hover>
                  <tbody>
                    <tr>
                      <th>Short Name</th>
                      <td>{source.short_name}</td>
                    </tr>
                    <tr>
                      <th>Coverage Area</th>
                      <td>{source.coverage_area || "Not specified"}</td>
                    </tr>
                    <tr>
                      <th>Update Frequency</th>
                      <td>{source.update_frequency || "Not specified"}</td>
                    </tr>
                    <tr>
                      <th>Resolution</th>
                      <td>{source.resolution || "Not specified"}</td>
                    </tr>
                    <tr>
                      <th>Source URL</th>
                      <td>
                        <a
                          href={source.src_url}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          {source.src_url}
                        </a>
                      </td>
                    </tr>
                    <tr>
                      <th>Last Updated</th>
                      <td>
                        {source.last_updated
                          ? new Date(source.last_updated).toLocaleString()
                          : "Never"}
                      </td>
                    </tr>
                  </tbody>
                </Table>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>
    </Container>
  );
};

export default Sources;