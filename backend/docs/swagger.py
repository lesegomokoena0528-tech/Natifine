"""
==========================================================
NatiFine REST API Documentation
==========================================================

Author  : Lesego Mokoena
Version : 1.0.0
OpenAPI : 3.0.3
==========================================================
"""

from flasgger import Swagger


swagger_template = {

    "openapi": "3.0.3",

    "info": {

        "title": "NatiFine REST API",

        "version": "1.0.0",

        "description": """
# NatiFine API

Production Ready Traffic Fine Management REST API.

---

## Features

- JWT Authentication
- Refresh Tokens
- Role-Based Access Control (RBAC)
- User Management
- Vehicle Management
- Traffic Fine Management
- Payments
- Disputes
- Notifications
- Dashboard Reporting
- Audit Logging
- Swagger Documentation

---

## Authentication

Most endpoints require a JWT access token.

Example:

""",

        "termsOfService":
            "https://natifine.co.za/terms",

        "contact": {

            "name": "NatiFine Development Team",

            "email": "support@natifine.co.za",

            "url": "https://natifine.co.za"

        },

        "license": {

            "name": "MIT",

            "url":
                "https://opensource.org/licenses/MIT"

        }

    },

    "externalDocs": {

        "description": "Developer Documentation",

        "url":
            "https://docs.natifine.co.za"

    },

    "servers": [

        {

            "url": "http://localhost:5000",

            "description": "Development"

        },

        {

            "url": "https://staging-api.natifine.co.za",

            "description": "Staging"

        },

        {

            "url": "https://api.natifine.co.za",

            "description": "Production"

        }

    ],

    "tags": [

        {
            "name": "Authentication",
            "description": "Authentication APIs"
        },

        {
            "name": "Users",
            "description": "User Management"
        },

        {
            "name": "Vehicles",
            "description": "Vehicle Management"
        },

        {
            "name": "Traffic Fines",
            "description": "Traffic Fine Management"
        },

        {
            "name": "Payments",
            "description": "Payment APIs"
        },

        {
            "name": "Disputes",
            "description": "Dispute APIs"
        },

        {
            "name": "Notifications",
            "description": "Notification APIs"
        },

        {
            "name": "Administration",
            "description": "Administration APIs"
        }

    ],

    "components": {

        "securitySchemes": {

            "BearerAuth": {

                "type": "http",

                "scheme": "bearer",

                "bearerFormat": "JWT"

            }

        },

        "schemas": {

            "ApiResponse": {

                "type": "object",

                "properties": {

                    "success": {

                        "type": "boolean"

                    },

                    "message": {

                        "type": "string"

                    },

                    "timestamp": {

                        "type": "string",

                        "format": "date-time"

                    },

                    "data": {

                        "type": "object"

                    }

                }

            },

            "ValidationError": {

                "type": "object",

                "properties": {

                    "success": {

                        "type": "boolean"

                    },

                    "message": {

                        "type": "string"

                    },

                    "errors": {

                        "type": "object"

                    }

                }

            }

        }

    },

    "security": [

        {

            "BearerAuth": []

        }

    ]

}


swagger_config = {

    "headers": [],

    "specs": [

        {

            "endpoint": "apispec",

            "route": "/apispec.json",

            "rule_filter": lambda rule: True,

            "model_filter": lambda tag: True

        }

    ],

    "swagger_ui": True,

    "specs_route": "/apidocs/",

    "static_url_path": "/flasgger_static",

    "swagger_ui_bundle_js":
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui-bundle.js",

    "swagger_ui_css":
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui.css"

}


def init_swagger(app):

    Swagger(

        app,

        template=swagger_template,

        config=swagger_config

    )
