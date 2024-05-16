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
