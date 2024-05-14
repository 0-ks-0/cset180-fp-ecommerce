function setOrderStatus(event, order_id)
{
	event.preventDefault()

	const status = (event.target.value).toLowerCase()

	fetch(`/orders/${order_id}`, {
		headers:
		{
			"Content-Type" : "application/json"
		},
		method: "PATCH",
		body: JSON.stringify({
			"status": status
		})
	})
	.then(function (response)
	{
		if (response.ok)
		{
			return response.json()

			.then(response =>
			{
				// const s = `input[value='${response.status}']`

				// const button = document.querySelector(`${s}`)

				// button.disabled = true

				alert(response.message)

				top.location = response.url
			})
		}
		else
		{
			throw Error(`Error: ${response.status || response.statusText}`)
		}
	})
	.catch(error =>
	{
		console.log(error)
	})

}
