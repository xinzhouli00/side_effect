import React, { useState, useEffect } from "react";

const DrugSideEffects_fda = ({ drugName }) => {
  const [data, setData] = useState(null); // Initial value is null
  const [isLoading, setIsLoading] = useState(true); // Loading state
  const [error, setError] = useState(null); // Error state

  useEffect(() => {
    // Fetch the data
    fetch("../data/formatted_drug_reactions.json") // Ensure the path is correct
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch data");
        }
        return response.json();
      })
      .then((jsonData) => {
        setData(jsonData);
        setIsLoading(false); // Data loaded successfully
      })
      .catch((err) => {
        setError(err.message); // Set error message
        setIsLoading(false);
      });
  }, []);

  // Show loading message while data is being fetched
  if (isLoading) {
    return <p>Loading...</p>;
  }

  // Show error message if fetching fails
  if (error) {
    return <p>Error: {error}</p>;
  }

  // Find the specified drug
  const filteredDrug = data.find((drug) => drug["drugName"] === drugName);

  // Show message if the drug is not found
  if (!filteredDrug) {
    return <p>Drug "{drugName}" not found.</p>;
  }

  // Sort side effects: descending order based on scores
  const sortedSideEffects = Object.entries(filteredDrug.sideEffects)
    .sort(([, scoreA], [, scoreB]) => parseFloat(scoreB) - parseFloat(scoreA)) // Sort by score in descending order
    .slice(0, 5); // Take the top 10

  // Render the content
  return (
    <div>
      <ul>
        {sortedSideEffects.map(([effect], index) => (
          <li key={effect}>
            {index + 1}. {effect}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default DrugSideEffects_fda;