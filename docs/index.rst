Welcome to quart-github-webhook's documentation!
=================================================

Very simple, but powerful, microframework for writing Github webhooks in Python.

.. code-block:: python

  from quart_github_webhook import Webhook
  from quart import Quart
  
  app = Quart(__name__)  # Standard Quart app
  webhook = Webhook(app) # Defines '/postreceive' endpoint
  
  @app.route("/")        # Standard Quart endpoint
  def hello_world():
      return "Hello, World!"
  
  @webhook.hook()        # Defines a handler for the 'push' event
  def on_push(data):
      print("Got push with: {0}".format(data))
  
  if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)

Contents:

.. toctree::
   :maxdepth: 1

   api_reference
   references
