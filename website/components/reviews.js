import React, { useEffect, useState } from 'react';

const DrugReviews = ({ drugName }) => {
  const [drugData, setDrugData] = useState(null);
  const [error, setError] = useState(null); // 用於處理錯誤
  const [expandedEffects, setExpandedEffects] = useState({}); // 用於追踪每個副作用的展開狀態

  useEffect(() => {
    // 動態載入 JSON 資料
    fetch('/data/reviews.json')
      .then((response) => {
        if (!response.ok) {
          throw new Error('Failed to fetch data');
        }
        return response.json();
      })
      .then((data) => {
        const drug = data.find((item) => item.drugName.toLowerCase() === drugName.toLowerCase());
        if (!drug) {
          throw new Error(`Drug "${drugName}" not found`);
        }
        setDrugData(drug);
      })
      .catch((error) => {
        console.error('Error loading drug data:', error);
        setError(error.message);
      });
  }, [drugName]);

  const toggleEffect = (effect) => {
    // 切換副作用的顯示狀態
    setExpandedEffects((prev) => ({
      ...prev,
      [effect]: !prev[effect],
    }));
  };

  if (error) {
    return <p style={{ color: 'red' }}>{error}</p>;
  }

  if (!drugData) {
    return (
      <div style={{ textAlign: 'center', marginTop: '50px' }}>
        <p>Loading...</p>
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div>
      {Object.entries(drugData.sideEffects).map(([sideEffect, comments]) => (
        <div key={sideEffect} style={{ marginBottom: '20px' }}>
          {/* 副作用標題 */}
          <h2
            onClick={() => toggleEffect(sideEffect)} // 點擊標題切換展開狀態
            style={{
              display: 'flex',
              alignItems: 'center',
              fontSize: '15px',
              cursor: 'pointer',
              color: '#007BFF',
            }}
          >
            {sideEffect}
          </h2>
          {/* 如果該副作用展開，顯示其評論 */}
          {expandedEffects[sideEffect] && (
            <div style={{ marginLeft: '20px', marginTop: '10px' }}>
              {comments.map((comment, index) => (
                <p key={index} style={{ fontStyle: 'italic', color: '#555' }}>
                  "{comment}"
                </p>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default DrugReviews;