/**
* @jsx React.DOM
*/

var $ = require('jquery');
var React = require('react');

module.exports = function (container, session) {
  var ClosePopupButton = React.createClass({
    handleClick: function (event) {
      event.preventDefault();
      window.close();
    },
    render: function() {
      if (! window.opener) {
        return null
      }
      return (
        <button className="btn btn-default" onClick={this.handleClick}>Close Window</button>
      );
    }
  });

  var IndexBox = React.createClass({    render: function() {
      return (
        <ClosePopupButton />
      );
    }
  });

  return React.renderComponent(
    <IndexBox />,
    container
  );
}
