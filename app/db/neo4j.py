from neo4j import GraphDatabase

_driver = None


def init_neo4j(app):
    global _driver
    _driver = GraphDatabase.driver(
        app.config["NEO4J_URI"],
        auth=(app.config["NEO4J_USER"], app.config["NEO4J_PASSWORD"]),
    )

    @app.teardown_appcontext
    def close(_):
        pass  # Driver is long-lived; close only on app shutdown


def get_driver():
    return _driver


def get_session():
    return _driver.session()
