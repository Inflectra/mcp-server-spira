from mcp.server.fastmcp import FastMCP


def register_prompt(mcp: FastMCP) -> None:
    
    @mcp.prompt(name="Create Conventions File", 
                description="Create a starting conventions file Inflectra Spira")
    def create_conventions_file() -> str:
        """
        Create a starting conventions file for Inflectra Spira.
        
        Use this prompt when you need to:
        - Generate a conventions file for Inflectra Spira
        - Get a template for project conventions
        - Start defining project standards and guidelines
        
        Returns:
            A formatted conventions file template
        """
        
        
        return """Create a concise Inflectra Spira conventions file to 
    serve as a quick reference for our environment. 
    This should capture all important patterns and structures 
    while remaining compact enough for an LLM context.

Using the available Inflectra Spira tools, please:

1. Get an overview of ALL programs (get_programs)
2. For ALL programs:
   - Get a list of all the milestones in the program (get_milestones)
   - Get a list of all the products in the program (get_program_products)
   - Get the list of releases in the product (get_releases) 
3. Capture template configuration for EACH product:
   - Template name and ID (get_product_template)
   - Artifact types and sub-types (get_artifact_types)
   - For each artifact type, get list of custom properties
     (get_custom_properties) and clearly identify mandatory fields

Create a concise markdown document with these sections:

1. **Workspaces**: 
    List of all programs and their products
2. **Template Configuration**: 
    Name, ID and description of product template
    List of all artifact types (requirement, test case, etc.),
    with the sub-types for each artifact nested underneath 
3. **Custom Properties**: 
    List of custom properties for each artifact type in the template
4. **Classification Structure**: 
    List of milestones in each program
    List of releases in each product

Focus on identifying and documenting patterns and 
variations between products. 
When listing field names or other details, prioritize the most important ones.
The goal is to create a reference that captures key conventions 
while staying concise."""
    