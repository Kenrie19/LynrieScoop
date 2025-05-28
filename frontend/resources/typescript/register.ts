document.getElementById('registerForm')?.addEventListener('submit', function (e) {
  e.preventDefault();

  const name = (document.getElementById('name') as HTMLInputElement).value;
  const email = (document.getElementById('email') as HTMLInputElement).value;
  const password = (document.getElementById('password') as HTMLInputElement).value;
  const confirmPassword = (document.getElementById('confirmPassword') as HTMLInputElement).value;

  if (password !== confirmPassword) {
    alert('Passwords do not match.');
    return;
  }

  // You can now send data to the server or store it locally
  console.log('Registering:', { name, email, password });
  alert('Registration successful!');
});
