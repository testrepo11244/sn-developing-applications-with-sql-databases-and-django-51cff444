from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Course, Question, Choice, Submission, Enrollment

@login_required
def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    
    if request.method == 'POST':
        score = 0
        questions = Question.objects.filter(course=course)
        total_marks = sum(q.mark for q in questions)
        
        for question in questions:
            selected_choice_id = request.POST.get(f'question_{question.id}')
            if selected_choice_id:
                choice = get_object_or_404(Choice, pk=selected_choice_id)
                if choice.is_correct:
                    score += question.mark
        
        Submission.objects.create(
            user=request.user,
            enrollment=enrollment,
            course=course,
            score=score
        )
        return redirect('show_exam_result', submission_id=Submission.objects.latest('submitted_at').id)
    
    questions = Question.objects.filter(course=course)
    return render(request, 'exam_form.html', {'course': course, 'questions': questions})

@login_required
def show_exam_result(request, submission_id):
    submission = get_object_or_404(Submission, pk=submission_id, user=request.user)
    course = submission.course
    
    # Calculate total possible marks for the context
    total_marks = sum(q.mark for q in Question.objects.filter(course=course))
    
    context = {
        'submission': submission,
        'course': course,
        'score': submission.score,
        'total_marks': total_marks,
        'percentage': (submission.score / total_marks * 100) if total_marks > 0 else 0,
    }
    return render(request, 'exam_result.html', context)