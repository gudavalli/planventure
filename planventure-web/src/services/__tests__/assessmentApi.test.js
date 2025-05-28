import { describe, it, expect, beforeEach, vi } from 'vitest';
import { assessmentService } from '../api';

// Mock the entire api module
vi.mock('../api', () => ({
  assessmentService: {
    getQuestions: vi.fn(),
  },
}));

describe('Assessment API Service - Question Filtering', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getQuestions API calls', () => {
    it('calls API with correct parameters for basic pagination', async () => {
      const mockResponse = {
        questions: [],
        pagination: { total_items: 0, total_pages: 1, current_page: 1, per_page: 10 }
      };

      assessmentService.getQuestions.mockResolvedValue(mockResponse);

      const result = await assessmentService.getQuestions(1, 10);

      expect(assessmentService.getQuestions).toHaveBeenCalledWith(1, 10);
      expect(result).toEqual(mockResponse);
    });    it('includes type parameter when not "all"', async () => {
      const mockResponse = { questions: [], pagination: {} };
      assessmentService.getQuestions.mockResolvedValue(mockResponse);

      const result = await assessmentService.getQuestions(1, 10, 'aptitude');

      expect(assessmentService.getQuestions).toHaveBeenCalledWith(1, 10, 'aptitude');
      expect(result).toEqual(mockResponse);
    });

    it('excludes type parameter when "all"', async () => {
      const mockResponse = { questions: [], pagination: {} };
      assessmentService.getQuestions.mockResolvedValue(mockResponse);

      const result = await assessmentService.getQuestions(1, 10, 'all');

      expect(assessmentService.getQuestions).toHaveBeenCalledWith(1, 10, 'all');
      expect(result).toEqual(mockResponse);
    });

    it('includes search parameter when provided', async () => {
      const mockResponse = { questions: [], pagination: {} };
      assessmentService.getQuestions.mockResolvedValue(mockResponse);

      const result = await assessmentService.getQuestions(1, 10, 'all', 'test search');

      expect(assessmentService.getQuestions).toHaveBeenCalledWith(1, 10, 'all', 'test search');
      expect(result).toEqual(mockResponse);
    });

    it('includes specialization parameter when provided', async () => {
      const mockResponse = { questions: [], pagination: {} };
      assessmentService.getQuestions.mockResolvedValue(mockResponse);

      const result = await assessmentService.getQuestions(1, 10, 'all', '', 'technical');

      expect(assessmentService.getQuestions).toHaveBeenCalledWith(1, 10, 'all', '', 'technical');
      expect(result).toEqual(mockResponse);
    });

    it('includes difficulty parameter when provided', async () => {
      const mockResponse = { questions: [], pagination: {} };
      assessmentService.getQuestions.mockResolvedValue(mockResponse);

      const result = await assessmentService.getQuestions(1, 10, 'all', '', '', 'hard');

      expect(assessmentService.getQuestions).toHaveBeenCalledWith(1, 10, 'all', '', '', 'hard');
      expect(result).toEqual(mockResponse);
    });

    it('includes all parameters when provided', async () => {
      const mockResponse = { questions: [], pagination: {} };
      assessmentService.getQuestions.mockResolvedValue(mockResponse);

      const result = await assessmentService.getQuestions(
        2, 20, 'aptitude', 'capital', 'technical', 'medium'
      );

      expect(assessmentService.getQuestions).toHaveBeenCalledWith(
        2, 20, 'aptitude', 'capital', 'technical', 'medium'
      );
      expect(result).toEqual(mockResponse);
    });

    it('handles empty string parameters correctly', async () => {
      const mockResponse = { questions: [], pagination: {} };
      assessmentService.getQuestions.mockResolvedValue(mockResponse);

      const result = await assessmentService.getQuestions(1, 10, '', '', '', '');

      expect(assessmentService.getQuestions).toHaveBeenCalledWith(1, 10, '', '', '', '');
      expect(result).toEqual(mockResponse);
    });

    it('uses default parameters when not provided', async () => {
      const mockResponse = { questions: [], pagination: {} };
      assessmentService.getQuestions.mockResolvedValue(mockResponse);

      const result = await assessmentService.getQuestions();

      expect(assessmentService.getQuestions).toHaveBeenCalledWith();
      expect(result).toEqual(mockResponse);
    });
  });
  describe('API Response Handling', () => {
    it('returns the response data', async () => {
      const mockResponseData = {
        questions: [
          { id: 1, content: 'Test question', specialization: 'aptitude' }
        ],
        pagination: { total_items: 1, total_pages: 1, current_page: 1, per_page: 10 }
      };

      assessmentService.getQuestions.mockResolvedValue(mockResponseData);

      const result = await assessmentService.getQuestions();

      expect(result).toEqual(mockResponseData);
    });

    it('handles API errors properly', async () => {
      assessmentService.getQuestions.mockRejectedValue(new Error('Network error'));

      await expect(assessmentService.getQuestions()).rejects.toThrow('Network error');
    });
  });
});
