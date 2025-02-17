import React from "react";
import Nav from "react-bootstrap/Nav";
import Navbar from "react-bootstrap/Navbar";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Form from "react-bootstrap/Form";
import { Switch, Route, withRouter } from "react-router-dom";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faGithub } from "@fortawesome/free-brands-svg-icons";

import ForecastView from "./ForecastView";
import LocationSearchField from "./LocationSearch";
import { Imperial, Metric } from "./Units";

import "./App.css";

class App extends React.Component {
  constructor(props) {
    super(props);
    // Initialize state with stored unit preference or default to Imperial
    const storedUnit = localStorage.getItem('temperatureUnit') || 'imperial';
    this.state = {
      location: null,
      unitConverter: storedUnit === 'imperial' ? new Imperial() : new Metric(),
      temperatureUnit: storedUnit
    };
  }

  toggleUnit = () => {
    const newUnit = this.state.temperatureUnit === 'imperial' ? 'metric' : 'imperial';
    const newConverter = newUnit === 'imperial' ? new Imperial() : new Metric();
    
    // Update state and persist to localStorage
    this.setState({
      unitConverter: newConverter,
      temperatureUnit: newUnit
    });
    localStorage.setItem('temperatureUnit', newUnit);
  };

  render() {
    if (this.props.location.pathname === "/" && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition((position) => {
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;

        this.props.history.push(`/coords/${lat}/${lon}`);
      });
    }

    const year = new Date().getFullYear();

    return (
      <div className="App">
        <Navbar bg="dark" variant="dark">
          <Navbar.Brand>Stratus - Demo App</Navbar.Brand>
          <Nav className="mr-auto"></Nav>

          <Form inline className="mr-3">
            <LocationSearchField
              onChange={(selected) => {
                const { id } = selected[0];
                this.props.history.push(`/id/${id}`);
              }}
            />
          </Form>
          <Form inline>
            <Form.Check
              type="switch"
              id="unit-toggle"
              label={this.state.temperatureUnit === 'imperial' ? "degF" : "degC"}
              checked={this.state.temperatureUnit === 'metric'}
              onChange={this.toggleUnit}
              className="text-light"
            />
          </Form>
        </Navbar>

        <Container style={{ marginTop: "1em" }}>
          <Switch>
            <Route
              path={`/id/:loc_id`}
              component={(props) => (
                <ForecastView converter={this.state.unitConverter} {...props} />
              )}
            />
            <Route
              path={`/coords/:lat/:lon`}
              component={(props) => (
                <ForecastView converter={this.state.unitConverter} {...props} />
              )}
            />

            <Route path="/">
              <Row className="justify-content-md-center">
                <Col md="auto">
                  <h4>Enter your location to get started</h4>
                </Col>
              </Row>
            </Route>
          </Switch>
        </Container>

        <footer className="footer">
          <Container fluid={true} style={{ height: "100%" }}>
            <Row className="h-100">
              <Col xs="4" className="align-self-center">
                <a
                  target="_blank"
                  rel="noopener noreferrer"
                  href="https://github.com/kallsyms/wx_explore"
                  className="text-muted"
                >
                  kallsyms/wx_explore on{" "}
                  <FontAwesomeIcon icon={faGithub} size="lg" />
                </a>
                <br />
                <span className="text-muted">&copy; {year}</span>
              </Col>

              <Col xs="8" className="align-self-center">
                <span
                  className="text-muted"
                  style={{
                    fontSize: "0.75em",
                    display: "block",
                    lineHeight: "1.5em",
                  }}
                >
                  The data on this website is best-effort, and no guarantees are
                  made about the availability or correctness of the data. It
                  should not be used for critical decision making.
                </span>
              </Col>
            </Row>
          </Container>
        </footer>
      </div>
    );
  }
}

export default withRouter(App);