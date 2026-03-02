// src/api.js
const BASE_URL = "http://localhost:8000/api";

export const fetchCandidates = async () => {
  try {
    const response = await fetch(`${BASE_URL}/candidates`);
    if (!response.ok) throw new Error("Network response was not ok");
    return await response.json();
  } catch (error) {
    console.error("Error fetching candidates:", error);
    return [];
  }
};

export const fetchDonations = async () => {
  try {
    const response = await fetch(`${BASE_URL}/donations`);
    if (!response.ok) throw new Error("Network response was not ok");
    return await response.json();
  } catch (error) {
    console.error("Error fetching donations:", error);
    return [];
  }
};

export const fetchDonors = async () => {
  try {
    const response = await fetch(`${BASE_URL}/donors`);
    if (!response.ok) throw new Error("Network response was not ok");
    return await response.json();
  } catch (error) {
    console.error("Error fetching donors:", error);
    return [];
  }
};