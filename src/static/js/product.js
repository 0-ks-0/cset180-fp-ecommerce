function deleteProduct(url, product_id)
{
	fetch(`${url}`, {
		headers:
		{
			"Accept": "application/json",
			"Content-Type" : "application/json"
		},
		method: "DELETE",
		body: JSON.stringify
		({
			"product_id": product_id
		})
	})
	.then(function (response) // Callback function when response sent from server
	{
		// Check if status code between 200 and 300
		if (response.ok)
		{
			return response.json() // Convert response from server to json

			.then(response =>
			{
				// Not working
				if(response.redirected)
				{
					window.location = response.url
				}

				window.location = response.response
			})
		}
		else
		{
			throw Error(`Error: ${response.status || response.statusText}`)
		}
	})
	.catch(error => // Catch errors from sending / receiving
	{
		console.log(error)
	})
}
