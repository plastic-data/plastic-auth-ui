/**
* @jsx React.DOM
*/

var $ = require('jquery');
var React = require('react');

module.exports = function (client_id, container, session, state) {
  var EmailField = React.createClass({
    render: function() {
      var error = this.props.error;
      var errorFeedback = error ? (
        <span className="glyphicon glyphicon-warning-sign form-control-feedback"></span>
      ) : null;
      var errorBlock = error ? (
        <span className="help-block">{error}</span>
      ) : null;

      return (
        <div className={'form-group' + (error ? ' has-feedback has-error' : '')}>
          <label className="control-label" htmlFor="email">Email</label>
          <input className="form-control" id="email" placeholder="Enter email" ref="email" required type="email" value={this.props.value} />
          {errorFeedback}
          {errorBlock}
        </div>
      );
    }
  });

  var PasswordField = React.createClass({
    render: function() {
      var error = this.props.error;
      var errorFeedback = error ? (
        <span className="glyphicon glyphicon-warning-sign form-control-feedback"></span>
      ) : null;
      var errorBlock = error ? (
        <span className="help-block">{error}</span>
      ) : null;

      return (
        <div className={'form-group' + (error ? ' has-feedback has-error' : '')}>
          <label className="control-label" htmlFor="password">Password</label>
          <input className="form-control" id="password" placeholder="Enter password" ref="password" required type="password" value={this.props.value} />
          {errorFeedback}
          {errorBlock}
        </div>
      );
    }
  });

  var SignInBox = React.createClass({
    getInitialState: function () {
      return {
        email: null,
        errors: null,
        session: session,
        password: null
      };
    },
    handleSubmit: function (event) {
      event.preventDefault();
      $.ajax('/api/1/authenticate', {
        data: {
          client_id: client_id,
          email: this.refs.emailField.refs.email.getDOMNode().value,
          password: this.refs.passwordField.refs.password.getDOMNode().value,
          synchronizer_token: this.state.session.synchronizer_token,
          state: state
        },
        dataType: 'json',
        type: 'POST'
      })
      .done(function (data, textStatus, jqXHR) {
          this.setState({
            errors: null,
            session: data.session
            });
          console.log('Authentication succeeded', data);
          // Redirect browser without and don't keep current page into history.
          window.location.replace('/');
      }.bind(this))
      .fail(function(jqXHR, textStatus, errorThrown) {
        try {
          var data = jqXHR.responseJSON;
          this.setState({
            errors: data.error.errors[0],
            session: data.session
          });
        } catch (error) {
          console.log(jqXHR);
          console.log(textStatus);
          console.log(errorThrown);
        }
      }.bind(this));
    },
    render: function() {
      var errors = this.state.errors || {};
      var errorBox = this.state.errors ? (
        <div className="alert alert-danger">
          <strong>Sign in failed!</strong> Please, correct the errors below.
        </div>
        ) : null;

      return (
        <form onSubmit={this.handleSubmit} role="form">
          {errorBox}
          <EmailField error={errors.email} ref="emailField" value={this.state.email}/>
          <PasswordField error={errors.password} ref="passwordField" value={this.state.password}/>
          <button className="btn btn-default" type="submit">Sign in</button>
        </form>
      );
    }
  });

  return React.renderComponent(
    <SignInBox />,
    container
  );
}
