const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function getHealth() {
  const response = await fetch(`${API_URL}/api/health`);

  if (!response.ok) {
    throw new Error("Error connecting to backend");
  }

  return response.json();
}