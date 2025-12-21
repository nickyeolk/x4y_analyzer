import { useState } from 'react';

export function AnalysisForm({ onSubmit, isLoading }) {
  const [xBrand, setXBrand] = useState('');
  const [yMarket, setYMarket] = useState('');
  const [description, setDescription] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (xBrand.trim() && yMarket.trim()) {
      onSubmit({
        x_brand: xBrand.trim(),
        y_market: yMarket.trim(),
        description: description.trim() || undefined,
      });
    }
  };

  const exampleIdeas = [
    { x_brand: 'Uber', y_market: 'Dog Walkers', description: 'On-demand dog walking service with real-time GPS tracking' },
    { x_brand: 'Netflix', y_market: 'Fitness Classes', description: 'Subscription-based on-demand fitness classes' },
    { x_brand: 'Airbnb', y_market: 'Office Spaces', description: 'Short-term office space rentals for remote workers' },
  ];

  const loadExample = (example) => {
    setXBrand(example.x_brand);
    setYMarket(example.y_market);
    setDescription(example.description);
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2>Analyze Your Startup Idea</h2>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label" htmlFor="xBrand">
            X Brand <span style={{ color: 'var(--error-color)' }}>*</span>
          </label>
          <input
            type="text"
            id="xBrand"
            className="form-input"
            placeholder="e.g., Uber, Netflix, Airbnb"
            value={xBrand}
            onChange={(e) => setXBrand(e.target.value)}
            disabled={isLoading}
            required
          />
          <small style={{ color: 'var(--gray-600)', fontSize: '0.875rem' }}>
            The established brand/company you want to emulate
          </small>
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="yMarket">
            Y Market <span style={{ color: 'var(--error-color)' }}>*</span>
          </label>
          <input
            type="text"
            id="yMarket"
            className="form-input"
            placeholder="e.g., Dog Walkers, Fitness Classes, Office Spaces"
            value={yMarket}
            onChange={(e) => setYMarket(e.target.value)}
            disabled={isLoading}
            required
          />
          <small style={{ color: 'var(--gray-600)', fontSize: '0.875rem' }}>
            The target market you want to apply the model to
          </small>
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="description">
            Description (Optional)
          </label>
          <textarea
            id="description"
            className="form-textarea"
            placeholder="Additional details about your idea..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            disabled={isLoading}
          />
        </div>

        <button
          type="submit"
          className="btn btn-primary btn-lg"
          disabled={isLoading || !xBrand.trim() || !yMarket.trim()}
        >
          {isLoading ? (
            <>
              <span className="spinner" style={{ width: '20px', height: '20px', borderWidth: '2px' }}></span>
              Analyzing...
            </>
          ) : (
            <>
              🚀 Analyze Idea
            </>
          )}
        </button>
      </form>

      {!isLoading && (
        <div style={{ marginTop: '2rem' }}>
          <p style={{ fontWeight: 600, marginBottom: '1rem', color: 'var(--gray-700)' }}>
            Try an example:
          </p>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            {exampleIdeas.map((idea, index) => (
              <button
                key={index}
                type="button"
                onClick={() => loadExample(idea)}
                className="btn"
                style={{
                  background: 'var(--gray-100)',
                  color: 'var(--gray-700)',
                  padding: '0.5rem 1rem',
                  fontSize: '0.875rem',
                }}
              >
                {idea.x_brand} for {idea.y_market}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
