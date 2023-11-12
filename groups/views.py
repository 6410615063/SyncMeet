from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages

from .models import Group, Post, GROUP_TAG, POST_TAG

@login_required
def create_group(request):
    if request.method == 'POST':
        gname = request.POST['gname']
        gdescription = request.POST['gdescription']
        gtag = request.POST['gtag']
        gprofile = request.FILES.get('gprofile')
        
        if gname and gdescription:
            new_group = Group.objects.create(
                gname=gname, 
                gdescription=gdescription, 
                gtag=gtag, 
                gprofile=gprofile,
                gcreator=request.user)
            new_group.gmembers.add(request.user)

            return redirect('group')
    return render(request, 'groups/create_group.html', {'GROUP_TAG': GROUP_TAG})

def group_schedule(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    return render(request, 'groups/group_schedule.html', {'group': group})

def group_members(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    members = group.gmembers.all()

    return render(request, 'groups/group_members.html', {'group': group, 'members': members})

def leave_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.method == 'POST':
        if request.user in group.gmembers.all():
            group.gmembers.remove(request.user)
            messages.success(request, "You have left the group.")
            return redirect('group')
        else:
            return HttpResponseForbidden("You are not a member of this group.")

    return HttpResponseForbidden("Invalid request.")

def post(request, group_id):
    tag_filter = request.GET.get('ptag', '')

    group = get_object_or_404(Group, id=group_id)
    posts = Post.objects.filter(pgroup_id=group_id, ptag__icontains=tag_filter).order_by('-pcreated_on')
    return render(request, 'groups/post.html', {'posts': posts, 'POST_TAG': POST_TAG, 'group': group})

def create_post(request, group_id):
    if request.method == 'POST':
        ptitle = request.POST['ptitle']
        pcontent = request.POST['pcontent']
        ptag = request.POST['ptag']
        group = get_object_or_404(Group, id=group_id)

        if ptitle and pcontent:
            Post.objects.create(
                ptitle=ptitle,
                pcontent=pcontent,
                ptag=ptag,
                pauthor=request.user,
                pgroup=group
            )
            return redirect('post', group_id=group.id)
    return render(request, 'groups/create_post.html', {'POST_TAG': POST_TAG, 'group': group})

def delete_post(request, group_id):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post = get_object_or_404(Post, id=post_id)

        if request.user != post.pauthor or group_id != post.pgroup_id:
            messages.error(request, "You don't have permission to delete this post.")
        else:
            post.delete()
            messages.success(request, "Post deleted successfully.")

    return redirect('post', group_id=group_id)