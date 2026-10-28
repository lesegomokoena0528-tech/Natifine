def test_register(client):

    response = client.post(

        "/api/auth/register",

        json={

            "id_number":"9901015009087",

            "first_name":"John",

            "last_name":"Smith",

            "email":"john@gmail.com",

            "phone":"0712345678",

            "password":"Password@123"

        }

    )

    assert response.status_code == 201