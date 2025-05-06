import random
from django.core.management.base import BaseCommand
from libros.models import CategoriaLibro, Libro

class Command(BaseCommand):
    help = 'Crea categorías y libros de prueba'

    def add_arguments(self, parser):
        parser.add_argument('--categorias', type=int, default=8, help='Número de categorías a crear')
        parser.add_argument('--libros', type=int, default=50, help='Número de libros a crear')

    def handle(self, *args, **options):
        # Datos de ejemplo para categorías
        categorias_data = [
            {
                'nombre': 'Literatura Clásica',
                'descripcion': 'Obras literarias de reconocido prestigio que han trascendido a lo largo del tiempo.'
            },
            {
                'nombre': 'Ciencia Ficción',
                'descripcion': 'Narrativa basada en elementos científicos pero de carácter imaginario.'
            },
            {
                'nombre': 'Historia',
                'descripcion': 'Libros sobre acontecimientos históricos y su análisis.'
            },
            {
                'nombre': 'Matemáticas',
                'descripcion': 'Textos sobre teoría matemática y sus aplicaciones.'
            },
            {
                'nombre': 'Física',
                'descripcion': 'Libros sobre principios y leyes físicas.'
            },
            {
                'nombre': 'Informática',
                'descripcion': 'Textos sobre programación, redes, sistemas operativos y tecnologías de la información.'
            },
            {
                'nombre': 'Biología',
                'descripcion': 'Libros sobre el estudio de los seres vivos y sus procesos.'
            },
            {
                'nombre': 'Química',
                'descripcion': 'Textos sobre la composición, estructura y propiedades de la materia.'
            },
            {
                'nombre': 'Economía',
                'descripcion': 'Libros sobre teorías económicas, mercados y finanzas.'
            },
            {
                'nombre': 'Psicología',
                'descripcion': 'Textos sobre el comportamiento humano y procesos mentales.'
            },
            {
                'nombre': 'Filosofía',
                'descripcion': 'Libros sobre el conocimiento, la existencia y el pensamiento crítico.'
            },
            {
                'nombre': 'Arte',
                'descripcion': 'Textos sobre historia del arte, técnicas artísticas y análisis estético.'
            }
        ]

        # Crear categorías
        categorias_creadas = []
        for i in range(min(options['categorias'], len(categorias_data))):
            categoria_info = categorias_data[i]
            categoria, created = CategoriaLibro.objects.get_or_create(
                nombre=categoria_info['nombre'],
                defaults={'descripcion': categoria_info['descripcion']}
            )
            categorias_creadas.append(categoria)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Categoría creada: {categoria.nombre}'))
            else:
                self.stdout.write(self.style.WARNING(f'Categoría ya existente: {categoria.nombre}'))

        # Datos de ejemplo para libros
        titulos = [
            "Cien años de soledad", "El señor de los anillos", "1984", "Don Quijote de la Mancha",
            "Rayuela", "Crimen y castigo", "Orgullo y prejuicio", "El principito", "Ficciones",
            "La metamorfosis", "Ulises", "En busca del tiempo perdido", "Moby Dick", "La Odisea",
            "La Ilíada", "Hamlet", "Romeo y Julieta", "Madame Bovary", "Los miserables",
            "Guerra y paz", "Ana Karenina", "El retrato de Dorian Gray", "Frankenstein",
            "Drácula", "El hobbit", "Fundación", "Neuromante", "Fahrenheit 451", "Un mundo feliz",
            "El nombre de la rosa", "El perfume", "El lobo estepario", "Siddharta", "El alquimista",
            "Crónica de una muerte anunciada", "El amor en los tiempos del cólera", "Pedro Páramo",
            "La región más transparente", "Rayuela", "La ciudad y los perros", "Conversación en La Catedral",
            "Sobre héroes y tumbas", "Adán Buenosayres", "Paradiso", "Grande Sertão: Veredas",
            "La casa verde", "El obsceno pájaro de la noche", "Los pasos perdidos", "El siglo de las luces",
            "La muerte de Artemio Cruz", "Cálculo Diferencial e Integral", "Física para Ciencias e Ingeniería",
            "Introducción a la Teoría de la Computación", "Biología Molecular de la Célula",
            "Principios de Química", "Macroeconomía", "Psicología Cognitiva", "Historia del Arte Occidental",
            "Introducción a la Filosofía", "Álgebra Lineal", "Estadística para Administración",
            "Anatomía Humana", "Derecho Constitucional", "Fundamentos de Marketing", "Sistemas Operativos Modernos"
        ]
        
        autores = [
            "Gabriel García Márquez", "J.R.R. Tolkien", "George Orwell", "Miguel de Cervantes",
            "Julio Cortázar", "Fiódor Dostoyevski", "Jane Austen", "Antoine de Saint-Exupéry",
            "Jorge Luis Borges", "Franz Kafka", "James Joyce", "Marcel Proust", "Herman Melville",
            "Homero", "William Shakespeare", "Gustave Flaubert", "Víctor Hugo", "León Tolstói",
            "Oscar Wilde", "Mary Shelley", "Bram Stoker", "Umberto Eco", "Patrick Süskind",
            "Hermann Hesse", "Paulo Coelho", "Mario Vargas Llosa", "Juan Rulfo", "Carlos Fuentes",
            "Ernesto Sábato", "Leopoldo Marechal", "José Lezama Lima", "João Guimarães Rosa",
            "José Donoso", "Alejo Carpentier", "Thomas Calculus", "Raymond A. Serway", "Michael Sipser",
            "Bruce Alberts", "Peter Atkins", "N. Gregory Mankiw", "Robert Sternberg", "H.W. Janson",
            "Karl Jaspers", "Gilbert Strang", "Richard Levin", "Frank H. Netter", "Hans Kelsen",
            "Philip Kotler", "Andrew S. Tanenbaum"
        ]
        
        editoriales = [
            "Penguin Random House", "HarperCollins", "Simon & Schuster", "Hachette Book Group",
            "Macmillan Publishers", "Scholastic", "Pearson Education", "McGraw-Hill Education",
            "Oxford University Press", "Cambridge University Press", "Wiley", "Springer",
            "Elsevier", "Taylor & Francis", "SAGE Publications", "Cengage Learning",
            "Planeta", "Santillana", "Anagrama", "Alfaguara", "Tusquets", "Seix Barral"
        ]

        # Crear libros
        for i in range(options['libros']):
            # Seleccionar datos aleatorios
            titulo = random.choice(titulos)
            autor = random.choice(autores)
            editorial = random.choice(editoriales)
            categoria = random.choice(categorias_creadas)
            stock = random.randint(1, 10)
            
            # Generar ISBN único
            isbn = f"978-{random.randint(0, 9)}-{random.randint(10000, 99999)}-{random.randint(100, 999)}-{random.randint(0, 9)}"
            
            # Evitar duplicados en títulos
            titulo_completo = f"{titulo} - {i}" if i > 0 else titulo
            
            # Crear libro
            libro, created = Libro.objects.get_or_create(
                isbn=isbn,
                defaults={
                    'titulo': titulo_completo,
                    'autor': autor,
                    'editorial': editorial,
                    'categoria': categoria,
                    'stock': stock
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Libro creado: {libro.titulo}'))
            else:
                self.stdout.write(self.style.WARNING(f'ISBN ya existente, se omitió: {isbn}'))

        self.stdout.write(self.style.SUCCESS('Libros creados exitosamente'))
