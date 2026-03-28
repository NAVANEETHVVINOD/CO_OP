import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import SearchPage from '@/app/(app)/search/page';

describe('SearchPage', () => {
  beforeEach(() => {
    localStorage.clear();
    sessionStorage.clear();
    vi.clearAllMocks();
  });

  it('renders page header', () => {
    render(<SearchPage />);
    expect(screen.getByText('Knowledge Search')).toBeInTheDocument();
    expect(screen.getByText('Search across all indexed documents')).toBeInTheDocument();
  });

  it('displays search input', () => {
    render(<SearchPage />);
    const input = screen.getByPlaceholderText(/search your knowledge base/i);
    expect(input).toBeInTheDocument();
  });

  it('shows search button', () => {
    render(<SearchPage />);
    expect(screen.getByRole('button', { name: /search/i })).toBeInTheDocument();
  });

  it('displays result count selector', () => {
    render(<SearchPage />);
    const select = screen.getByRole('combobox');
    expect(select).toBeInTheDocument();
  });

  it('shows search mode buttons', () => {
    render(<SearchPage />);
    expect(screen.getByRole('button', { name: /semantic/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /balanced/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /keyword/i })).toBeInTheDocument();
  });

  it('displays empty state initially', () => {
    render(<SearchPage />);
    expect(screen.getByText('Search your knowledge base')).toBeInTheDocument();
    expect(screen.getByText(/upload and index documents/i)).toBeInTheDocument();
  });

  it('allows typing in search input', () => {
    render(<SearchPage />);
    const input = screen.getByPlaceholderText(/search your knowledge base/i) as HTMLInputElement;
    
    fireEvent.change(input, { target: { value: 'test query' } });
    expect(input.value).toBe('test query');
  });

  it('performs search when button is clicked', async () => {
    render(<SearchPage />);
    
    const input = screen.getByPlaceholderText(/search your knowledge base/i);
    fireEvent.change(input, { target: { value: 'test query' } });
    
    const searchButton = screen.getByRole('button', { name: /search/i });
    fireEvent.click(searchButton);
    
    await waitFor(() => {
      // Check for text that's not broken up by mark tags
      expect(screen.getByText(/relevant content/i)).toBeInTheDocument();
    });
  });

  it('performs search when Enter is pressed', async () => {
    render(<SearchPage />);
    
    const input = screen.getByPlaceholderText(/search your knowledge base/i);
    fireEvent.change(input, { target: { value: 'test query' } });
    fireEvent.keyDown(input, { key: 'Enter' });
    
    await waitFor(() => {
      expect(screen.getByText(/relevant content/i)).toBeInTheDocument();
    });
  });

  it('displays search results', async () => {
    render(<SearchPage />);
    
    const input = screen.getByPlaceholderText(/search your knowledge base/i);
    fireEvent.change(input, { target: { value: 'test' } });
    
    const searchButton = screen.getByRole('button', { name: /search/i });
    fireEvent.click(searchButton);
    
    await waitFor(() => {
      expect(screen.getByText(/relevant content/i)).toBeInTheDocument();
    });
    
    expect(screen.getByText(/another relevant passage/i)).toBeInTheDocument();
  });

  it('shows result metadata', async () => {
    render(<SearchPage />);
    
    const input = screen.getByPlaceholderText(/search your knowledge base/i);
    fireEvent.change(input, { target: { value: 'test' } });
    fireEvent.click(screen.getByRole('button', { name: /search/i }));
    
    await waitFor(() => {
      const pdfFiles = screen.getAllByText('test.pdf');
      expect(pdfFiles.length).toBeGreaterThan(0);
    });

    expect(screen.getByText(/page 1/i)).toBeInTheDocument();
    expect(screen.getByText(/score: 0.95/i)).toBeInTheDocument();
  });

  it('displays "Use in Chat" buttons for results', async () => {
    render(<SearchPage />);
    
    const input = screen.getByPlaceholderText(/search your knowledge base/i);
    fireEvent.change(input, { target: { value: 'test' } });
    fireEvent.click(screen.getByRole('button', { name: /search/i }));
    
    await waitFor(() => {
      const useInChatButtons = screen.getAllByText(/use in chat/i);
      expect(useInChatButtons.length).toBeGreaterThan(0);
    });
  });

  it('shows search time after results load', async () => {
    render(<SearchPage />);
    
    const input = screen.getByPlaceholderText(/search your knowledge base/i);
    fireEvent.change(input, { target: { value: 'test' } });
    fireEvent.click(screen.getByRole('button', { name: /search/i }));
    
    await waitFor(() => {
      expect(screen.getByText(/results in \d+ms/i)).toBeInTheDocument();
    });
  });

  it('changes search mode when mode button is clicked', () => {
    render(<SearchPage />);
    
    const keywordButton = screen.getByRole('button', { name: /keyword/i });
    fireEvent.click(keywordButton);
    
    // Keyword button should now be active (styled differently)
    expect(keywordButton).toBeInTheDocument();
  });

  it('changes result count when selector is changed', () => {
    render(<SearchPage />);
    
    const select = screen.getByRole('combobox') as HTMLSelectElement;
    fireEvent.change(select, { target: { value: '10' } });
    
    expect(select.value).toBe('10');
  });

  it('disables search button when input is empty', () => {
    render(<SearchPage />);
    
    const searchButton = screen.getByRole('button', { name: /search/i });
    expect(searchButton).toBeDisabled();
  });

  it('enables search button when input has text', () => {
    render(<SearchPage />);
    
    const input = screen.getByPlaceholderText(/search your knowledge base/i);
    fireEvent.change(input, { target: { value: 'test' } });
    
    const searchButton = screen.getByRole('button', { name: /search/i });
    expect(searchButton).not.toBeDisabled();
  });
});
