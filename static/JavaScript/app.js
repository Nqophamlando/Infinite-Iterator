// Function to validate the registration form
function validateRegistrationForm() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const email = document.getElementById('email').value;

    // Check if username, password, and email are filled
    if (username === "" || password === "" || email === "") {
        alert("All fields must be filled out");
        return false;
    }
    
    // Simple email validation (not comprehensive)
    const emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
    if (!email.match(emailPattern)) {
        alert("Please enter a valid email address");
        return false;
    }
    
    return true;
}

// Function to confirm a vote submission
function confirmVote() {
    const confirmVote = confirm("Are you sure you want to submit your vote?");
    return confirmVote;  
}

// Add event listener to the vote form submit button
const voteForm = document.getElementById('vote-form');
if (voteForm) {
    voteForm.addEventListener('submit', function(event) {
        if (!confirmVote()) {
            event.preventDefault();  
        }
    });
}

// Add dynamic behavior to show a success message after voting
const voteButton = document.getElementById('vote-button');
if (voteButton) {
    voteButton.addEventListener('click', function() {
        alert("Your vote has been successfully submitted!");
    });
}
