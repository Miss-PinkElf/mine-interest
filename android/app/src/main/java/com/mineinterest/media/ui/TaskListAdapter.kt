package com.mineinterest.media.ui

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.mineinterest.media.core.model.MediaTask
import com.mineinterest.media.databinding.ItemTaskBinding

class TaskListAdapter : ListAdapter<MediaTask, TaskListAdapter.Holder>(Diff) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): Holder {
        val binding = ItemTaskBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return Holder(binding)
    }

    override fun onBindViewHolder(holder: Holder, position: Int) {
        holder.bind(getItem(position))
    }

    class Holder(
        private val binding: ItemTaskBinding,
    ) : RecyclerView.ViewHolder(binding.root) {
        fun bind(task: MediaTask) {
            binding.taskTitle.text = task.displayTitle ?: task.sourceText.take(40)
            binding.taskPlatform.text = task.platform.name
            binding.taskStatus.text = "${task.status} ${task.progressPercent}%"
            binding.taskMessage.text = listOfNotNull(task.message, task.outputPath)
                .joinToString("\n")
                .ifBlank { "—" }
        }
    }

    private object Diff : DiffUtil.ItemCallback<MediaTask>() {
        override fun areItemsTheSame(oldItem: MediaTask, newItem: MediaTask): Boolean =
            oldItem.id == newItem.id

        override fun areContentsTheSame(oldItem: MediaTask, newItem: MediaTask): Boolean =
            oldItem == newItem
    }
}
