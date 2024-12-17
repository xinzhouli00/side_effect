import React, { useState, useEffect } from "react";
import Link from "next/link"; // 使用 Next.js 的 Link

const SideEffectToDrugs = () => {
  const [data, setData] = useState([]);
  const [sideEffectsList, setSideEffectsList] = useState([]);
  const [selectedSideEffect, setSelectedSideEffect] = useState("");
  const [topDrugs, setTopDrugs] = useState([]);
  const [bottomDrugs, setBottomDrugs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("../data/drugSideEffectsData.json")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to load data");
        }
        return response.json();
      })
      .then((jsonData) => {
        setData(jsonData);
        setIsLoading(false);

        const allSideEffects = new Set();
        jsonData.forEach((drug) => {
          Object.keys(drug.sideEffects).forEach((effect) =>
            allSideEffects.add(effect)
          );
        });
        setSideEffectsList([...allSideEffects]);
      })
      .catch((err) => {
        setError(err.message);
        setIsLoading(false);
      });
  }, []);

  const handleSearch = () => {
    if (!selectedSideEffect) return;

    const results = data
      .map((drug) => {
        const score = drug.sideEffects[selectedSideEffect] || null;
        return score ? { drugName: drug.drugName, score: parseFloat(score) } : null;
      })
      .filter(Boolean)
      .sort((a, b) => b.score - a.score);

    setTopDrugs(results.slice(0, 3));
    setBottomDrugs(results.slice(-3).reverse());
  };

  const tableStyles = {
    borderCollapse: "collapse",
    width: "100%",
    marginTop: "20px",
  };

  const thStyles = {
    border: "1px solid #ddd",
    padding: "10px",
    textAlign: "center",
    backgroundColor: "#f4f4f4",
    fontWeight: "bold",
  };

  const tdStyles = {
    border: "1px solid #ddd",
    padding: "10px",
    textAlign: "center",
  };

  const containerStyles = {
    maxWidth: "800px",
    margin: "0 auto",
    padding: "20px",
    fontFamily: "Arial, sans-serif",
  };

  const loadingStyles = {
    textAlign: "center",
    fontSize: "18px",
    color: "#555",
  };

  const errorStyles = {
    color: "red",
    fontWeight: "bold",
    textAlign: "center",
  };

  if (isLoading) {
    return <p style={loadingStyles}>Loading data...</p>;
  }

  if (error) {
    return <p style={errorStyles}>Error: {error}</p>;
  }

  return (
    <div style={containerStyles}>
      <div>
        <label htmlFor="sideEffect" style={{ marginRight: "10px" }}>
          Select a Side Effect:
        </label>
        <select
          id="sideEffect"
          value={selectedSideEffect}
          onChange={(e) => setSelectedSideEffect(e.target.value)}
          style={{
            padding: "8px",
            borderRadius: "4px",
            border: "1px solid #ddd",
            marginRight: "10px",
          }}
        >
          <option value="">-- Select a Side Effect --</option>
          {sideEffectsList.map((effect) => (
            <option key={effect} value={effect}>
              {effect}
            </option>
          ))}
        </select>
        <button
          onClick={handleSearch}
          disabled={!selectedSideEffect}
          style={{
            padding: "8px 16px",
            backgroundColor: selectedSideEffect ? "#007BFF" : "#ccc",
            color: "#fff",
            border: "none",
            borderRadius: "4px",
            cursor: selectedSideEffect ? "pointer" : "not-allowed",
          }}
        >
          Search
        </button>
      </div>

      {topDrugs.length > 0 || bottomDrugs.length > 0 ? (
        <div>
          <h2 style={{ marginTop: "20px" }}>
            Top 3 Drugs related to "{selectedSideEffect}":
          </h2>
          <table style={tableStyles}>
            <thead>
              <tr>
                <th style={thStyles}>Rank</th>
                <th style={thStyles}>Drug Name</th>
              </tr>
            </thead>
            <tbody>
              {topDrugs.map((drug, index) => (
                <tr key={drug.drugName}>
                  <td style={tdStyles}>{index + 1}</td>
                  <td style={tdStyles}>
                    <Link
                      href={`/medicine/${encodeURIComponent(drug.drugName)}`}
                      style={{ color: "#007BFF", textDecoration: "none" }}
                    >
                      {drug.drugName}
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <h2 style={{ marginTop: "20px" }}>
            Bottom 3 Drugs related to "{selectedSideEffect}":
          </h2>
          <table style={tableStyles}>
            <thead>
              <tr>
                <th style={thStyles}>Rank</th>
                <th style={thStyles}>Drug Name</th>
              </tr>
            </thead>
            <tbody>
              {bottomDrugs.map((drug, index) => (
                <tr key={drug.drugName}>
                  <td style={tdStyles}>{index + 1}</td>
                  <td style={tdStyles}>
                    <Link
                      href={`/medicine/${encodeURIComponent(drug.drugName)}`}
                      style={{ color: "#007BFF", textDecoration: "none" }}
                    >
                      {drug.drugName}
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        selectedSideEffect && (
          <p style={{ marginTop: "20px", fontSize: "16px" }}>
            No drugs found for side effect "{selectedSideEffect}".
          </p>
        )
      )}
    </div>
  );
};

export default SideEffectToDrugs;