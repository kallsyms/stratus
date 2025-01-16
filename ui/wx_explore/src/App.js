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
import { Imperial } from "./Units";

import "./App.css";

class App extends React.Component {
  state = {
    location: null,
    unitConverter: new Imperial(),
    geoError: null,
    isGeoLoading: false
  };

  componentDidMount() {
    if (this.props.location.pathname === "/" && navigator.geolocation) {
      this.getGeolocation();
    }
  }

  getGeolocation = () => {
    this.setState({ isGeoLoading: true, geoError: null });
    
    const geoOptions = {
      timeout: 10000,
      maximumAge: 0,
      enableHighAccuracy: true
    };

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;
        this.setState({ isGeoLoading: false });
        this.props.history.push(`/coords/${lat}/${lon}`);
      },
      (error) => {
        let errorMessage = "Unable to get your location";
        switch(error.code) {
          case error.PERMISSION_DENIED:
            errorMessage = "Location access was denied. Please enable location services or search for your location manually.";
            break;
          case error.POSITION_UNAVAILABLE:
            errorMessage = "Location information is unavailable. Please try again or search manually.";
            break;
          case error.TIMEOUT:
            errorMessage = "Location request timed out. Please try again or search manually.";
            break;
          default:
            errorMessage = "An unknown error occurred getting your location. Please try again or search manually.";
        }
        this.setState({ geoError: errorMessage, isGeoLoading: false });
      },
      geoOptions
    );
  }

  render() {
    if (this.props.location.pathname === "/" && navigator.geolocation && !this.state.geoError && !this.state.isGeoLoading) {
      this.getGeolocation();
    }

    const year = new Date().getFullYear();

    return (
      <div className="App">
        <Navbar bg="dark" variant="dark">
          <Navbar.Brand>Stratus - Demo App</Navbar.Brand>
          <Nav className="mr-auto"></Nav>

          <Form inline>
            <LocationSearchField
              onChange={(selected) => {
                const { id } = selected[0];
                this.props.history.push(`/id/${id}`);
              }}
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
                  {this.state.isGeoLoading ? (
                    <h4>Getting your location...</h4>
                  ) : this.state.geoError ? (
                    <div className="text-center">
                      <h4 className="text-danger mb-3">{this.state.geoError}</h4>
                      <h5>Enter your location in the search bar above to get started</h5>
                    </div>
                  ) : !navigator.geolocation ? (
                    <div className="text-center">
                      <h4 className="text-warning mb-3">Location services are not available in your browser</h4>
                      <h5>Please use the search bar above to find your location</h5>
                    </div>
                  ) : (
                    <h4>Enter your location to get started</h4>
                  )}
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