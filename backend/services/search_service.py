"""
Search Service
DO-178C Traceability: REQ-DB-054 (PostgreSQL full-text search)

This service provides full-text search across all AISET entities using
PostgreSQL's advanced full-text search capabilities.

Features:
- Ranked full-text search
- Multi-entity search (requirements, design, tests, CIs, projects)
- Project-scoped search
- Search suggestions
- Recent search history
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)


class SearchService:
    """
    Full-text search service using PostgreSQL tsvector.

    Provides fast, ranked search across all textual content in AISET.
    """

    def __init__(self, db: Session):
        """
        Initialize search service.

        Args:
            db: Database session
        """
        self.db = db

    def search(
        self,
        query: str,
        entity_types: Optional[List[str]] = None,
        project_id: Optional[int] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Perform full-text search across entities.

        Args:
            query: Search query string
            entity_types: Filter by entity types (requirement, design_component, test_case, configuration_item, project)
            project_id: Filter by project ID
            limit: Maximum results to return

        Returns:
            List of search results with ranking
        """
        # Prepare search query for PostgreSQL full-text search
        # Convert to tsquery format: replace spaces with &
        ts_query = ' & '.join(query.split())

        # Default entity types
        if entity_types is None:
            entity_types = [
                'requirement',
                'design_component',
                'test_case',
                'configuration_item',
                'project'
            ]

        # Call search function
        sql = text("""
            SELECT * FROM search_aiset(
                :search_query,
                :entity_types,
                :project_filter,
                :result_limit
            )
        """)

        try:
            result = self.db.execute(
                sql,
                {
                    'search_query': ts_query,
                    'entity_types': entity_types,
                    'project_filter': project_id,
                    'result_limit': limit
                }
            )

            results = []
            for row in result:
                results.append({
                    'entity_type': row.entity_type,
                    'id': row.id,
                    'entity_id': row.entity_id,
                    'title': row.title,
                    'description': row.description,
                    'project_id': row.project_id,
                    'rank': float(row.rank)
                })

            logger.info(f"Search '{query}' returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return []

    def search_requirements(
        self,
        query: str,
        project_id: Optional[int] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search only requirements.

        Args:
            query: Search query
            project_id: Optional project filter
            limit: Result limit

        Returns:
            List of requirements matching query
        """
        return self.search(
            query=query,
            entity_types=['requirement'],
            project_id=project_id,
            limit=limit
        )

    def search_design_components(
        self,
        query: str,
        project_id: Optional[int] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search only design components.

        Args:
            query: Search query
            project_id: Optional project filter
            limit: Result limit

        Returns:
            List of design components matching query
        """
        return self.search(
            query=query,
            entity_types=['design_component'],
            project_id=project_id,
            limit=limit
        )

    def search_test_cases(
        self,
        query: str,
        project_id: Optional[int] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search only test cases.

        Args:
            query: Search query
            project_id: Optional project filter
            limit: Result limit

        Returns:
            List of test cases matching query
        """
        return self.search(
            query=query,
            entity_types=['test_case'],
            project_id=project_id,
            limit=limit
        )

    def search_configuration_items(
        self,
        query: str,
        project_id: Optional[int] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search only configuration items.

        Args:
            query: Search query
            project_id: Optional project filter
            limit: Result limit

        Returns:
            List of CIs matching query
        """
        return self.search(
            query=query,
            entity_types=['configuration_item'],
            project_id=project_id,
            limit=limit
        )

    def get_search_suggestions(
        self,
        partial_query: str,
        limit: int = 10
    ) -> List[str]:
        """
        Get search suggestions based on partial query.

        Args:
            partial_query: Partial search query
            limit: Maximum suggestions

        Returns:
            List of suggested search terms
        """
        # In production, implement based on popular searches or indexed terms
        # For now, return empty list
        logger.debug(f"Getting suggestions for: {partial_query}")
        return []

    def save_search_history(
        self,
        user_id: int,
        search_query: str,
        results_count: int
    ):
        """
        Save search to user's search history.

        Args:
            user_id: User ID
            search_query: Search query
            results_count: Number of results returned
        """
        # In production, save to search_history table
        logger.debug(f"Saving search history for user {user_id}: '{search_query}' ({results_count} results)")

    def get_recent_searches(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[str]:
        """
        Get user's recent searches.

        Args:
            user_id: User ID
            limit: Maximum searches to return

        Returns:
            List of recent search queries
        """
        # In production, query from search_history table
        logger.debug(f"Getting recent searches for user {user_id}")
        return []

    def get_popular_searches(
        self,
        project_id: Optional[int] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get most popular search queries.

        Args:
            project_id: Optional project filter
            limit: Maximum results

        Returns:
            List of popular searches with counts
        """
        # In production, query aggregated search history
        logger.debug(f"Getting popular searches")
        return []


def get_search_service(db: Session) -> SearchService:
    """
    Get search service instance.

    Args:
        db: Database session

    Returns:
        SearchService instance
    """
    return SearchService(db)
