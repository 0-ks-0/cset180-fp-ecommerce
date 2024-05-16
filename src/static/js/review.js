function createReviewImage()
{
	// Container for image
	const imageContainer = document.createElement("div")
	imageContainer.classList.add("image_container")
	imageContainer.classList.add("flex_row")

	// Input for image
	const input = document.createElement("input")
	input.setAttribute("type", "text")
	input.name = "review_image"
	input.placeholder = "Image"
	input.required = true

	// Button to delete image
	const deleteButton = document.createElement("button")
	deleteButton.classList.add("delete_button")
	deleteButton.innerHTML = "Delete"
	deleteButton.onclick = () =>
	{
		deleteButton.parentElement.remove()
	}

	imageContainer.appendChild(input)
	imageContainer.appendChild(deleteButton)

	const form = document.querySelector("#review_form")
	const addButton = document.querySelector("#add_reivew_image_button")

	form.insertBefore(imageContainer, addButton)
}

function submitReview(event, product_id)
{
	event.preventDefault()

	const data = {}

	data.id = product_id

	data.rating = document.getElementsByName("rating")[0].value

	data.description = document.getElementsByName("description")[0].value

	// Images
	const image_inputs = document.getElementsByName("review_image")

	const images = []

	for (const input of image_inputs)
	{
		images.push(input.value)
	}

	data.images = images

	console.log(data)

	fetch(`/products//${product_id}`, {
		headers:
		{
			"Content-Type" : "application/json"
		},
		method: "POST",
		body: JSON.stringify(data)
	})
	.then(function (response) // Callback function when response sent from server
	{
		// Check if status code between 200 and 300
		if (response.ok)
		{
			return response.json() // Convert response from server to json

			.then(response =>
			{
				top.location = response.url
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
